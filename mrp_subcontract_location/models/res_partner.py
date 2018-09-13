# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_supplier_wh_and_location(self):
        self.ensure_one()
        supplier_wh = self.env['stock.warehouse'].search(
            [('partner_id', '=', self.id)], limit=1)
        return supplier_wh, supplier_wh.lot_stock_id
