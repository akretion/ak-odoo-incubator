# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
from functools import lru_cache

import werkzeug.datastructures

import odoo
from odoo import http
from odoo.tools import date_utils

from odoo.addons.fastapi.fastapi_dispatcher import FastApiDispatcher

_logger = logging.getLogger(__name__)


class FastapiRootPaths:
    _root_paths_by_db = {}

    @classmethod
    def set_root_paths(cls, db, root_paths):
        cls._root_paths_by_db[db] = root_paths
        cls.is_fastapi_path.cache_clear()

    @classmethod
    @lru_cache(maxsize=1024)
    def is_fastapi_path(cls, db, path):
        return any(
            path.startswith(root_path)
            for root_path in cls._root_paths_by_db.get(db, [])
        )


class FastapiRequest(http.WebRequest):
    _request_type = "fastapi"

    def __init__(self, *args):
        super().__init__(*args)
        self.params = {}
        self._dispatcher = FastApiDispatcher(self)

    def make_response(self, data, headers=None, cookies=None, status=200):
        """Helper for non-HTML responses, or HTML responses with custom
        response headers or cookies.

        While handlers can just return the HTML markup of a page they want to
        send as a string if non-HTML data is returned they need to create a
        complete response object, or the returned data will not be correctly
        interpreted by the clients.

        :param basestring data: response body
        :param headers: HTTP headers to set on the response
        :type headers: ``[(name, value)]``
        :param collections.abc.Mapping cookies: cookies to set on the client
        """
        response = http.Response(data, status=status, headers=headers)
        if cookies:
            for k, v in cookies.items():
                response.set_cookie(k, v)
        return response

    def make_json_response(self, data, headers=None, cookies=None, status=200):
        """Helper for JSON responses, it json-serializes ``data`` and
        sets the Content-Type header accordingly if none is provided.

        :param data: the data that will be json-serialized into the response body
        :param int status: http status code
        :param List[(str, str)] headers: HTTP headers to set on the response
        :param collections.abc.Mapping cookies: cookies to set on the client
        :rtype: :class:`~odoo.http.Response`
        """
        data = json.dumps(data, ensure_ascii=False, default=date_utils.json_default)

        headers = werkzeug.datastructures.Headers(headers)
        headers["Content-Length"] = len(data)
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json; charset=utf-8"

        return self.make_response(data, headers.to_wsgi_list(), cookies, status)

    def dispatch(self):
        return self._dispatcher.dispatch(None, None)

    def _handle_exception(self, exception):
        _logger.exception(
            "Exception during fastapi request handling", exc_info=exception
        )
        return self._dispatcher.handle_error(exception)


ori_get_request = http.root.__class__.get_request


def get_request(self, httprequest):
    db = httprequest.session.db
    if db and odoo.service.db.exp_db_exist(db):
        # on the very first request processed by a worker,
        # registry is not loaded yet
        # so we enforce its loading here.
        odoo.registry(db)
        if FastapiRootPaths.is_fastapi_path(db, httprequest.path):
            if "/payment/providers/monetico/webhook" in httprequest.path:
                # TODO FIXME
                # /!\ we read the values here so after the values are not empty
                _logger.info("webhook with values %s", httprequest.values)
            return FastapiRequest(httprequest)
    return ori_get_request(self, httprequest)


http.root.__class__.get_request = get_request
