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


# TODO when creating inter wh rules : make the last one in make to order by default + put partner_address_id
class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

#    @api.model
#    def create(self, vals):
#        wh = super(StockWarehouse, self).create(vals)
#        if vals.get('partner_id'):
#            wh.create_inter_wh_rule()
#        return wh

#    def write(self, vals):
#        res = super(StockWarehouse, self).write(vals)
#        for wh in self:
#            if vals.get('partner_id'):
#                wh.create_inter_wh_rule()
#        return res

#    def create_inter_wh_rule(self):
#        self.ensure_one()
#        inter_wh_route = self.env.ref(
#            'mrp_subcontract_location.route_interwarehouse_supply')
#        wh_inter_wh_supply_rule_vals = {
#            'action': 'move',
#            'warehouse_id': self.id,
#            'name': 'Transit => %s' % self.code,
#            'location_id': self.partner_id.reception_location_id.id,
#            'location_src_id': self.env.ref('stock.stock_location_inter_wh').id,
#            'picking_type_id': self.in_type_id.id,
#            'propagate': True,
#            'procure_method': 'make_to_order',
#            'route_id': inter_wh_route.id,
##            'partner_address_id': self.partner_id.id,
#        }
#        self.env['procurement.rule'].create(
#            wh_inter_wh_supply_rule_vals)

    def create_resupply_routes(self, supplier_warehouses, default_resupply_wh):
        res = super(StockWarehouse, self).create_resupply_routes(supplier_warehouses, default_resupply_wh)
        Pull = self.env['procurement.rule']
        mto_route = self._get_mto_route()

        input_location, output_location = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        internal_transit_location, external_transit_location = self._get_transit_locations()

        for supplier_wh in supplier_warehouses:
            transit_location = internal_transit_location if supplier_wh.company_id == self.company_id else external_transit_location
            if not transit_location:
                continue
            output_location = supplier_wh.lot_stock_id if supplier_wh.delivery_steps == 'ship_only' else supplier_wh.wh_output_stock_loc_id
            rules = Pull.search([
                ['warehouse_id', '=', supplier_wh.id],
                ['location_id','=',  transit_location.id],
                ['location_src_id', '=', output_location.id],
                ['route_id', '!=', False],
                ['partner_address_id', '=', False],
            ])
            if len(rules)==2:
                rule = [rule for rule in rules if rule.route_id != mto_route][0]
                next_rule = (rule.route_id.pull_ids - rule)
                partner_1 = next_rule.warehouse_id.partner_id
                partner_2 = rule.warehouse_id.partner_id
                rules.write({'partner_address_id': partner_1.id })
                next_rule.partner_address_id = partner_2.id
            else:
                print "too many rules !"
        return res