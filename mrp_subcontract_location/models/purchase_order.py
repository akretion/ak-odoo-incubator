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

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id',
        string='Warehouse',
        help="Technical field used to display the Drop Ship Address",
        readonly=True)

    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        for purchase in self:
            all_moves_in = self.env['stock.move']
            all_moves_out = self.env['stock.move']
            location = self._get_location()
            for line in purchase.order_line:
                if line._is_service_procurement():
                    mo = line.procurement_ids.production_id

                    mo.update_locations(location)
                    moves_in, moves_in_prod = mo.add_moves_before_production(
                        location)
                    moves_out, moves_out_prod = mo.add_moves_after_production(
                        location)
                    all_moves_in |= moves_in
                    all_moves_out |= moves_out

                    # faut-til cabler les in et les outs ?
                    # ou alors le in suivant ? (facturation)
                    self.add_purchase_line_id(moves_out, line)
                    self.add_purchase_line_id(moves_in, line)
            self.attach_picking_in(all_moves_in)
            self.attach_picking_out(all_moves_out)
        return res

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

    def add_purchase_line_id(self, moves, line):
        '''Add the reference to this PO.
        Only moves in the picking
        '''
        self.ensure_one()
        moves.write({'purchase_line_id': line.id})

    def attach_picking_out(self, moves):
        inter_co = self.env.ref(
            'stock.stock_location_inter_wh'
        )
        ins = {}
        outs = {}
        for move in moves:
            if move.move_dest_id.location_id != inter_co:
                continue
            # can happen now for pull rule move creation...
#            if move.move_dest_id.picking_id:
#                _logger.warning('devrait pas arriver')
#                continue
            move.move_dest_id.partner_id = self.partner_id
            move.partner_id = (
                move.move_dest_id.picking_type_id.warehouse_id.partner_id)
            key = move.move_dest_id.location_dest_id
            ins.setdefault(key, self.env['stock.move'])
            outs.setdefault(key, self.env['stock.move'])
            if not move.picking_id:
                ins[key] |= move
            if not move.move_dest_id.picking_id:
                outs[key] |= move.move_dest_id

        for key, moves in ins.iteritems():
            if moves:
                picking_in = self.env['stock.picking'].create(
                    moves[0]._get_new_picking_values())
                moves.write({'picking_id': picking_in.id})

        for key, moves in outs.iteritems():
            if moves:
                picking_in = self.env['stock.picking'].create(
                    moves[0]._get_new_picking_values())
                moves.write({'picking_id': picking_in.id})

    def attach_picking_in(self, moves):
        inter_co = self.env.ref(
            'stock.stock_location_inter_wh'
        )
        ins = {}
        outs = {}
        for move in moves:
            if move.move_orig_ids.location_dest_id != inter_co:
                continue
            if move.move_orig_ids.picking_id:
                _logger.warning('devrait pas arriver')
                continue
            move.move_orig_ids.partner_id = self.partner_id
            move.partner_id = (
                move.move_orig_ids.picking_type_id.warehouse_id.partner_id)
            key = move.move_orig_ids.location_id
            ins.setdefault(key, self.env['stock.move'])
            outs.setdefault(key, self.env['stock.move'])
            ins[key] |= move.move_orig_ids
            outs[key] |= move

        for key, moves in ins.iteritems():
            picking_in = self.env['stock.picking'].create(
                moves[0]._get_new_picking_values())
            moves.write({'picking_id': picking_in.id})

        for key, moves in outs.iteritems():
            picking_in = self.env['stock.picking'].create(
                moves[0]._get_new_picking_values())
            moves.write({'picking_id': picking_in.id})
