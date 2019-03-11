# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_supplier_wh_and_location(self):
        self.ensure_one()
        supplier_wh = self.env['stock.warehouse'].search(
            [('partner_id', 'in', (self | self.child_ids).ids)], limit=1)
        return supplier_wh, supplier_wh.lot_stock_id
