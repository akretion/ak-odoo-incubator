# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    date_printed = fields.Datetime()

    @api.multi
    def set_printed(self):
        now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return self.write({'date_printed': now})
