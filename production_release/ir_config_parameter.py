# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def set_param(self, key, value, groups=None):
        if groups is None:
            groups = []
        # Buildout native recipe anybox compatibility
        if key == 'buildout.db_version':
            self.env['production.release'].create({
                'name': value,
                'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                })
        return super(IrConfigParameter, self).set_param(
            key, value, groups=groups)
