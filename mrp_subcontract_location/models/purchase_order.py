# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

#    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id',
#        string='Warehouse',
#        help="Technical field used to display the Drop Ship Address",
#        readonly=True)

    def manage_subcontracted_manufacture_line(self, line):
        self.ensure_one()
        supplier = self.partner_id
        if line._is_service_procurement():
            mo = line.mo_id
            supplier_wh, supplier_loc = supplier.\
                _get_supplier_wh_and_location()
            if mo.location_dest_id != supplier_loc:
                mo.update_locations(supplier_wh, supplier_loc)
                moves_in = mo.update_moves_before_production(
                    supplier, supplier_wh, supplier_loc)
                moves_out, moves_out_dest = (
                    mo.update_moves_after_production(
                        supplier, supplier_wh, supplier_loc)
                )
            else:
                # in order to link existing move to po
                moves_in = self.env['stock.move']
                moves_out, moves_out_dest = (
                    mo.get_expedition_and_reception_moves()
                )

            # po.picking_type_id (Supplier/manufacture)
            # TODO: externalise it on the po level instead of line
            self.picking_type_id = supplier_wh.manu_type_id.id

            # faut-til cabler les in et les outs ?
            # ou alors le in suivant ? (facturation)
            self.add_purchase_line_id(moves_out, line)
            self.add_purchase_line_id(moves_out_dest, line)
            return moves_in, moves_out, moves_out_dest

    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        for purchase in self:
            for line in purchase.order_line:
                # In seperate method as it is reused in an other module
                purchase.manage_subcontracted_manufacture_line(line)
        return res

    def add_purchase_line_id(self, moves, line):
        '''Add the reference to this PO.
        Only moves in the picking
        '''
        self.ensure_one()
        moves.write({'purchase_line_id': line.id})

#    def attach_picking_out(self, moves):
#        inter_co = self.env.ref(
#            'stock.stock_location_inter_wh'
#        )
#        all_moves = self.env['stock.move']
#        for move in moves:
#            # TODO find a best and more secure way to do this?!
#            next_po = move.move_dest_id.move_dest_id.raw_material_production_id.service_procurement_id.purchase_id
#            if next_po and next_po.state not in ('purchase', 'done'):
#                continue
#            elif move.location_dest_id.usage == 'customer':
#                # TODO need some actions?
#                continue
#            else:
#                move.move_dest_id.partner_id = self.partner_id.id
#                move.partner_id = (
#                    move.move_dest_id.picking_type_id.warehouse_id.partner_id.id)
#                all_moves |= move
#                all_moves |= move.move_dest_id
#                # Handle case it was in picking before
#                # TODO maybe we should find a way to block creation at first place?
#                pickings = all_moves.mapped('picking_id')
#                all_moves.write({'picking_id': False})
#                for picking in pickings:
#                    if not picking.move_lines:
#                        picking.unlink()
#                all_moves.assign_picking_by_purchase()


#    def attach_picking_in(self, moves):
#        inter_co = self.env.ref(
#            'stock.stock_location_inter_wh'
#        )
#        all_moves = self.env['stock.move']
#        for move in moves:
#            previous_po = move.purchase_line_id.order_id
#            if not previous_po or previous_po.state not in ('purchase', 'done'):
#                continue
#            if move.move_orig_ids.picking_id:
#                _logger.warning('devrait pas arriver')
#                continue
#            move.move_orig_ids.partner_id = self.partner_id
#            move.partner_id = (
#                previous_po.partner_id.id)

#            all_moves |= move
#            all_moves |= move.move_orig_ids
#            # Handle case it was in picking before
#            # TODO maybe we should find a way to block creation at first place?
#            pickings = all_moves.mapped('picking_id')
#            all_moves.write({'picking_id': False})
#            for picking in pickings:
#                if not picking.move_lines:
#                    picking.unlink()

#            all_moves.assign_picking_by_purchase()
