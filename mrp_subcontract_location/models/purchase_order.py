# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id',
        string='Warehouse',
        help="Technical field used to display the Drop Ship Address",
        readonly=True)

    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        for purchase in self:
            location = self._get_location()
            picking_in = self.create_picking_in(location)
            picking_out = self.create_picking_out(location)
            for line in purchase.order_line:
                if line._is_service_procurement():
                    mo = line.procurement_ids.production_id
                    mo.update_locations(location)
                    moves_in, moves_in_prod = mo.add_moves_before_production(
                        location, picking_in)
                    moves_out, moves_out_prod = mo.add_moves_after_production(
                        location, picking_out)

    @api.multi
    def _get_location(self):
        self.ensure_one()
        return self.partner_id.supplier_location_id

    @api.multi
    def _get_destination_location(self):
        # TODO: toujours d'actu ?
        self.ensure_one()
        supplier_wh = self.env.ref(
            'mrp_subcontract_location.warehouse_supplier')
        if supplier_wh.id == self.warehouse_id.id and self.dest_address_id:
            if not self.dest_address_id.supplier_location_id:
                raise exceptions.ValidationError(
                    _('No location configured on the subcontractor'))
            return self.dest_address_id.supplier_location_id.id
        else:
            return super(PurchaseOrder, self)._get_destination_location()

    def create_picking_in(self, location):
        return self.env['stock.picking'].create({
            'picking_type_id': location.get_warehouse().in_type_id.id,
            'location_id': self.env.ref(
                'stock.stock_location_inter_wh').id,
            'location_dest_id': location.id,
        })

    def create_picking_out(self, location):
        return self.env['stock.picking'].create({
            'picking_type_id': location.get_warehouse().out_type_id.id,
            'location_id': location.id,
            'location_dest_id': self.env.ref(
                'stock.stock_location_inter_wh').id,
        })
