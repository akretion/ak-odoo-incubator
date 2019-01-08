# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo.http import Controller, request, route
from odoo.addons.base_rest.controllers import main
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class ExternalTaskController(main.RestController):
    _root_path = '/project-api/'
    _collection_name = 'project.project'
    _default_auth = 'api_key'

    @classmethod
    def _get_partner_from_request(cls):
        auth_api_key = getattr(request, 'auth_api_key', None)
        if auth_api_key:
            partner =  request.env['res.partner'].search([(
                'project_auth_api_key_id', '=', auth_api_key.id
            )])
            if partner:
                return partner
        raise AccessError('No partner match the API KEY')

    def _get_component_context(self):
        """
        This method adds the component context:
        * the partner
        * the project
        """
        res = super(ExternalTaskController, self)._get_component_context()
        res['partner'] = self._get_partner_from_request()
        return res
