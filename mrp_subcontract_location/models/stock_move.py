# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _search_picking_for_assignation(self):
        # if no PO, group by procurement group
        # if PO, put all moves in the same picking
        self.ensure_one()
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_dest_id.id),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'in', [
                'draft', 'confirmed', 'waiting',
                'partially_available', 'assigned'])
        ]
        if not self.purchase_line_id:
            domain.append(('group_id', '=', self.group_id.id))
            return self.env['stock.picking'].search(domain, limit=1)
        domain.append((
            'purchase_id', '=', self.purchase_line_id.order_id.id)
        )
        candidates = self.env['stock.picking'].search(domain, order="id")
        short_list = self.env['stock.picking']
        for candidate in candidates:
            move_lines = candidate.move_lines
            po_line_ids = move_lines.mapped('purchase_line_id')
            orders = po_line_ids.mapped('order_id')

            # ensure all lines have the same purchase_line_id
            not_bought = move_lines.filtered(
                lambda m: not m.purchase_line_id)

            # ensure no line has no purchase_line_id
            all_same_po = len(orders) == 1
            if all_same_po and len(not_bought) == 0:
                short_list |= candidate
                break
        return short_list[:1]

    @api.multi
    def assign_picking(self):
        Picking = self.env['stock.picking']
        # we want to group moves per supplier (receipt and ship)
        # The moves are created before the purchase orders,
        # while nohting in purchased we want to group ber procurement
        # group.
        # when a PO is confiremd, we want to have all the related moves
        # in a single picking.
        # no super because the picking search in super don't
        # care about the partner_id

        # mig v12: remove this function since search_picking_for_assignation
        # is in core
        candidates_for_empty_picking = []
        for move in self:
            recompute = False
            if move.picking_id:
                candidates_for_empty_picking.append(move.picking_id)
            picking = move._search_picking_for_assignation()
            if not picking:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            if recompute:
                move.recompute()
        for picking in candidates_for_empty_picking:
            if not picking.move_lines:
                picking.unlink()
        return True
