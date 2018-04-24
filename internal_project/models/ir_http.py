# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Unauthorized

from openerp import models
from openerp.http import request
import logging

_logger = logging.getLogger(__name__)


class IrHttp(models.Model):
    _inherit = 'ir.http'

    def _auth_method_externaltask(self):
        headers = request.httprequest.environ
        if headers.get('HTTP_API_KEY'):
            request.uid = 1
            project = request.env['project.project'].search(
                [('api_key', '=', headers['HTTP_API_KEY'])])
            if len(project) == 1:
                request.project = project
                return True
        _logger.error("Wrong HTTP_API_KEY, access denied")
        raise Unauthorized("Wrong HTTP_API_KEY, access denied")
