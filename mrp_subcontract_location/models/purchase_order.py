# -*- coding: utf-8 -*- 
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, exceptions, _
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
            mo = line.procurement_ids.production_id
            supplier_wh, supplier_loc = self.partner_id.\
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

            # faut-til cabler les in et les outs ?
            # ou alors le in suivant ? (facturation)
            self.add_purchase_line_id(moves_out, line)
            self.add_purchase_line_id(moves_out_dest, line)
            return moves_in, moves_out, moves_out_dest

    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        for purchase in self:
#            all_moves_in = self.env['stock.move']
#            all_moves_out = self.env['stock.move']
#            location = self._get_location()
#            supplier = purchase.partner_id
            for line in purchase.order_line:
                # In seperate method as it is reused in an other module
                purchase.manage_subcontracted_manufacture_line(line)
#                if line._is_service_procurement():
#                    mo = line.procurement_ids.production_id
#                    if mo.location_dest_id != purchase.partner_id.location_id:
#                        mo.update_locations(supplier)
#                        moves_in = mo.update_moves_before_production(
#                            supplier)
#                        moves_out, moves_out_dest = (
#                            mo.update_moves_after_production(
#                                supplier)
#                        )
##                        all_moves_in |= moves_in
##                        all_moves_out |= moves_out

#                    # faut-til cabler les in et les outs ?
#                    # ou alors le in suivant ? (facturation)
#                    self.add_purchase_line_id(moves_out, line)
#                    self.add_purchase_line_id(moves_out_dest, line)
#            self.attach_picking_in(all_moves_in)
#            self.attach_picking_out(all_moves_out)
        return res

#    @api.multi
#    def _get_location(self):
#        self.ensure_one()
#        return self.partner_id.supplier_location_id

#    @api.multi
#    def _get_destination_location(self):
#        # TODO: toujours d'actu ?
#        self.ensure_one()
#        supplier_wh = self.env.ref(
#            'mrp_subcontract_location.warehouse_supplier')
#        if supplier_wh.id == self.warehouse_id.id and self.dest_address_id:
#            if not self.dest_address_id.supplier_location_id:
#                raise exceptions.ValidationError(
#                    _('No location configured on the subcontractor'))
#            return self.dest_address_id.supplier_location_id.id
#        else:
#            return super(PurchaseOrder, self)._get_destination_location()

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
