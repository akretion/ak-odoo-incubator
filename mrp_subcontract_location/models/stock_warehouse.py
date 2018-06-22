# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def create(self, vals):
        wh = super(StockWarehouse, self).create(vals)
        if vals.get('partner_id'):
            wh.create_inter_wh_rule()
        return wh

    def write(self, vals):
        res = super(StockWarehouse, self).write(vals)
        # TODO maybe add field on warehouse to link the rule and manage creation/deletion
        for wh in self:
            if vals.get('partner_id'):
                wh.create_inter_wh_rule()
        return res

    def create_inter_wh_rule(self):
        self.ensure_one()
        inter_wh_route = self.env.ref(
            'mrp_subcontract_location.route_interwarehouse_supply')
        wh_inter_wh_supply_rule_vals = {
            'action': 'move',
            'name': 'Transit => %s' % self.code,
            'location_id': self.lot_stock_id.id,
            'location_src_id': self.env.ref('stock.stock_location_inter_wh').id,
            'picking_type_id': self.in_type_id.id,
            'propagate_warehouse_id': self.env.ref('stock.warehouse0').id,
            'propagate': True,
            'procure_method': 'make_to_stock',
            'route_id': inter_wh_route.id,
            'partner_address_id': self.partner_id,
        }
        self.env['procurement.rule'].create(
            wh_inter_wh_supply_rule_vals)
