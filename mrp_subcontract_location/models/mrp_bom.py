# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def get_supplied_wh(self):
        """Warehouse where the OF will take place by default."""
        return self.picking_type_id.warehouse_id

    @api.multi
    def ensure_manufacture_route(self):
        """Add manufacture and remove buy route on product."""
        manuf_route_id = self.env.ref('mrp.route_warehouse0_manufacture').id
        buy_route_id = self.env.ref('purchase.route_warehouse0_buy').id
        for bom in self:
            product = bom.product_tmpl_id
            product_route_ids = product.route_ids.ids
            route_vals = []
            if buy_route_id in product_route_ids:
                # remove buy from product route
                route_vals.append((3, buy_route_id, 0))
            if manuf_route_id not in product_route_ids:
                # adds manufacture from product_route
                route_vals.append((4, manuf_route_id, 0))
            if route_vals:
                product.write({'route_ids': route_vals})

    @api.model
    def compute_product_routes_cron(self):
        boms = self.env['mrp.bom'].search([])
        boms.check_and_set_product_routes()

    @api.model
    def _get_supply_route(self, supplied_wh, supply_wh):
        """Get or create supply route between warehouses"""
        # TODO move it to stock_route file ?
        route_obj = self.env['stock.location.route']
        route = route_obj.search([
            ('supplied_wh_id', '=', supplied_wh.id),
            ('supplier_wh_id', '=', supply_wh.id)])
        if not route:
            # Check the box on warehouse to create the route
            # (4, id, 0) seems to be buggy...
            # when adding a new route on the UI, Odoo make a
            # (6, 0, ids), let do the same.
            resupply_whs_ids = supplied_wh.resupply_wh_ids.ids
            resupply_whs_ids.append(supply_wh.id)
            vals = {
                'resupply_wh_ids': [(6, 0, resupply_whs_ids)]
            }
            supplied_wh.write(vals)
            route = route_obj.search([
                ('supplied_wh_id', '=', supplied_wh.id),
                ('supplier_wh_id', '=', supply_wh.id)])
            if not route:
                _logger.warning(
                    "resupply route problem for wh %s"
                    % supplied_wh.id)
                return False
        return route
    
    def _check_same_wh(self, supply_wh, supplied_wh):
        return supply_wh == supplied_wh
    

    def check_and_set_product_routes(self):
        """
            Recompute inter warehouse routes for all boms.

        Buy and Manufcature routes should be set correctly on each product.
        For manufactured products, vendors should be set on the service
        This function will add needing inter warehouse routes.
        """
        manuf_route_id = self.env.ref('mrp.route_warehouse0_manufacture').id
        for bom in self:
            # TODO: shall we do that ?
            bom.ensure_manufacture_route()
            supplied_wh = bom.get_supplied_wh()
            if not supplied_wh:
                continue
            
            manuf_products = bom.bom_line_ids.mapped("product_id").filtered(lambda p: manuf_route_id in p.route_ids.ids)     
            if not manuf_products:
                product = bom.product_tmpl_id
                supply_wh = self.env["stock.warehouse"].search([("partner_id", "=", product.main_supplierinfo_id.name.id)], limit=1)
                if not supply_wh:
                    continue
                if self._check_same_wh(supply_wh, supplied_wh):
                        continue
                self._set_product_routes(product=product, supply_wh=supply_wh, supplied_wh=supplied_wh)
            else:
                for line in bom.bom_line_ids:
                    product = line.product_id
                    if manuf_route_id not in product.route_ids.ids:
                        # Product must be bought, ignore it
                        continue
                    line_bom = product.bom_ids and product.bom_ids[0] or False
                    # Config error, raise something?
                    if not line_bom:
                        _logger.warning(
                            "error : no bom found for component %s from "
                            "bom %s" % (product.default_code, bom.id,)
                        )
                        continue
                    supply_wh = line_bom.get_supplied_wh() 
                    if not supply_wh:
                            continue
                    if self._check_same_wh(supply_wh, supplied_wh):
                            continue
                    self._set_product_routes(product=product, supply_wh=supply_wh, supplied_wh=supplied_wh)
    
    def _set_product_routes(self, product, supply_wh, supplied_wh):
        product_routes = product.route_ids
        route = self._get_supply_route(supplied_wh, supply_wh)
        if route.id not in product_routes.ids:
            # Check if there is already an interwh route bringing the
            # product to the same wh. If this is the case, we erase
            # it from the product. Indeed we can't have 2 routes
            # bringing the product to the same wh, as Odoo won't know
            # which to choose.
            prod_vals = {
                'route_ids': []
            }
            same_supplied_wh_routes = product_routes.filtered(
                lambda r: r.supplied_wh_id == supplied_wh)
            if same_supplied_wh_routes:
                remove_routes = [
                    (3, x.id, 0) for x in same_supplied_wh_routes
                ]
                prod_vals['route_ids'] += remove_routes
            prod_vals['route_ids'].append((4, route.id, 0))
            product.write(prod_vals)
