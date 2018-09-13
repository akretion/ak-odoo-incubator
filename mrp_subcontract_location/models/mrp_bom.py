# -*- coding: utf-8 -*-

from odoo import api, models, fields, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'


    def get_bom_supplier(self):
        self.ensure_one()
        if self.service_id:
            supplier_info_bom = self.service_id.seller_ids
            supplier_bom = supplier_info_bom and supplier_info_bom[0].name \
                           or False
        else:
            # Manufactured internally, but I guess we still has to set
            # multi wh routes...
            supplier_bom = self.env.ref('base.main_partner')
        return supplier_bom

    def check_manufacture_buy_route(self, buy_route_id, manuf_route_id):
        self.ensure_one()
        product = self.product_tmpl_id
        product_route_ids = product.route_ids.ids
        route_vals = []
        if buy_route_id in product_route_ids:
            route_vals.append((3, buy_route_id, 0))
        if not manuf_route_id in product_route_ids:
            route_vals.append((4, manuf_route_id, 0))
        if route_vals:
            product.write({'route_ids': route_vals})

    @api.model
    def compute_product_routes_cron(self):
        boms = self.env['mrp.bom'].search([])
        boms.check_and_set_product_routes()

    def check_and_set_product_routes(self):
        """
            Recompute inter warehouse routes for all components of the bom
        """
        manuf_route_id = self.env.ref('mrp.route_warehouse0_manufacture').id
        buy_route_id = self.env.ref('purchase.route_warehouse0_buy').id
        wh_obj = self.env['stock.warehouse']
        route_obj = self.env['stock.location.route']
        for bom in self:
            bom.check_manufacture_buy_route(buy_route_id, manuf_route_id)
            supplier_bom = bom.get_bom_supplier()
            if not supplier_bom:
                _logger.info("error : no supplier for bom %s" % bom.id)
                continue
            supplied_wh = wh_obj.search(
                [('partner_id', '=', supplier_bom.id)], limit=1)
            if not supplied_wh:
                _logger.info("error : no wh found for supplier %s"
                             % supplier_bom.id)
                continue
            for line in bom.bom_line_ids:
                product = line.product_id
                product_routes = product.route_ids
                if not manuf_route_id in product_routes.ids:
                    # Product must be bought, ignore it
                    continue
                line_bom = product.bom_ids and product.bom_ids[0] or False
                # Config error, raise something?
                if not line_bom:
                    _logger.info("error : no bom found for component %s from "
                                 "bom %s" % (product.default_code, bom.id,))
                line_supplier = line_bom.get_bom_supplier()
                # Config error, raise something?
                if not line_supplier:
                    print line_bom.product_id.name
                    continue
                    _logger.info("error : no supplier for bom %s"
                                 % line_bom.id)
                supply_wh = wh_obj.search(
                    [('partner_id', '=', line_supplier.id)], limit=1)
                if not supply_wh:
                    _logger.info("error : no wh found for supplier %s"
                                 % line_supplier.id)
                    continue
                # Product and raw material are manufactured in the same wh
                # no need for inter wh routes.
                if supply_wh == supplied_wh:
                    continue

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
                        _logger.info("resupply route problem for wh %s"
                                     % supplied_wh.id)
                        continue
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
