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


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _search_picking_for_assignation(self):
        self.ensure_one()
        return self.env['stock.picking'].search([
            ('partner_id', '=', self.partner_id.id),
            ('group_id', '=', self.group_id.id),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_dest_id.id),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'in', [
                'draft', 'confirmed', 'waiting',
                'partially_available', 'assigned'])], limit=1)

    @api.multi
    def assign_picking(self):
        Picking = self.env['stock.picking']
        # we want to group moves per supplier (receipt and ship)
        # and per command (group.id)
        # no super because the picking search in super don't
        # care about the partner_id

        # mig v12: remove this function since search_picking_for_assignation
        # is in core
        for move in self:
            recompute = False
            picking = move._search_picking_for_assignation()
            if not picking:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            if recompute:
                move.recompute()
        return True
