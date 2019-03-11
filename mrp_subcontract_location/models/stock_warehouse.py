# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
import logging

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def create_resupply_routes(
        self, supplier_warehouses, default_resupply_wh
    ):
        res = super(StockWarehouse, self).create_resupply_routes(
            supplier_warehouses, default_resupply_wh)
        Pull = self.env['procurement.rule']
        mto_route = self._get_mto_route()

        input_location, output_location = self._get_input_output_locations(
            self.reception_steps, self.delivery_steps)
        internal_transit_location, external_transit_location = (
            self._get_transit_locations())

        for supplier_wh in supplier_warehouses:
            transit_location = (
                internal_transit_location
                if supplier_wh.company_id == self.company_id
                else external_transit_location
            )
            if not transit_location:
                continue
            output_location = (
                supplier_wh.lot_stock_id
                if supplier_wh.delivery_steps == 'ship_only'
                else supplier_wh.wh_output_stock_loc_id
            )
            rules = Pull.search([
                ['warehouse_id', '=', supplier_wh.id],
                ['location_id', '=', transit_location.id],
                ['location_src_id', '=', output_location.id],
                ['route_id', '!=', False],
                ['partner_address_id', '=', False],
            ])
            if len(rules) == 2:
                rule = (
                    [rule for rule in rules if rule.route_id != mto_route]
                )[0]
                next_rule = (rule.route_id.pull_ids - rule)
                partner_1 = next_rule.warehouse_id.partner_id
                partner_2 = rule.warehouse_id.partner_id
                rules.write({'partner_address_id': partner_1.id})
                next_rule.partner_address_id = partner_2.id
            else:
                _logger.warning("create_resupply_routes: too many rules !")
        return res
