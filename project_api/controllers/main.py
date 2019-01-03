# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo.http import Controller, request, route
from odoo.addons.base_rest.controllers import main

_logger = logging.getLogger(__name__)


class ExternalTaskController(main.RestController):
    _root_path = '/externaltask/'
    _collection_name = 'project.project'
    _default_auth = 'api_key'

    @classmethod
    def _get_project_from_request(cls):
        auth_api_key = getattr(request, 'auth_api_key', None)
        project_model = request.env['project.project']
        if auth_api_key:
            return project_model.search([(
                'auth_api_key_id', '=', auth_api_key.id
            )])
        return project_model.browse([])

    def _get_component_context(self):
        """
        This method adds the component context:
        * the partner
        * the project
        """
        res = super(ExternalTaskController, self)._get_component_context()
        headers = request.httprequest.environ
#        res['partner'] = self._get_partner_from_headers(headers)
        res['project'] = self._get_project_from_request()
        return res

    @route([
        '<string:_service_name>/read',
    ], methods=['GET'])
    def read(self, _service_name, **params):
        return self._process_method(_service_name, 'read', params=params)

    @route([
        '<string:_service_name>/read_group',
    ], methods=['GET'])
    def read_group(self, _service_name, **params):
        return self._process_method(_service_name, 'read_group', params=params)


    @route(
        '/externaltask/message', methods=['GET', 'POST'], auth="externaltask")
    def message_list(self, **params):
        method = request.httprequest.method
        service = request.env['task.service']
        service.project = request.project
        if method == 'GET':
            res = service.get_message(params)
        elif method == 'POST':
            res = service.create_message(params)
        return request.make_response(res)
