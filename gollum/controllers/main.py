# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug.exceptions import Unauthorized
from werkzeug.datastructures import FileStorage
from odoo.http import request
from odoo import http
import requests
import logging

_logger = logging.getLogger(__name__)

try:
    from unidecode import unidecode
except:
    _logger.debug('Cannot `import unidecode`.')


class GollumController(http.Controller):

    @http.route('/wiki', methods=['GET'], auth="user")
    def wiki(self, *args, **kwargs):
        return http.local_redirect('/wiki/home')

    @http.route('/wiki/<path:path>', methods=['GET', 'DELETE', 'PUT', 'POST'],
                auth="user", csrf=False)
    def proxy(self, *args, **kwargs):
        method = request.httprequest.method
        base_path = request.env['ir.config_parameter'].get_param('gollum_path')
        url = base_path + "/wiki/%s" % kwargs.pop('path')
        user = request.env.user
        if user.has_group('gollum.group_gollum_edit'):
            access = 'edit'
        else:
            access = 'read'
        headers = {
            'access': access,
            'user': unidecode(user.name),
            'email': user.email,
            }
        post_files = {}
        for k, v in kwargs.copy().iteritems():
            if isinstance(v, FileStorage):
                p_file = kwargs.pop(k)
                post_files[k] = (
                    p_file.filename, p_file.stream,
                    p_file.mimetype, headers)
        if method == 'GET':
            res = requests.get(url, data=kwargs, headers=headers)
        elif method == 'POST' and access == 'edit':
            res = requests.post(
                url, data=kwargs, headers=headers, files=post_files)
        elif method == 'DELETE' and access == 'edit':
            res = requests.delete(url, data=kwargs, headers=headers)
        else:
            raise Unauthorized("Your user do not have right access")
        return request.make_response(res.content, headers=res.headers.items())
