# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_state = fields.Selection([
        ('unprocessed', 'Unprocessed'),
        ('partially', 'Partially'),
        ('done', 'Done')],
        compute='_compute_picking_state',
        string='Picking state',

    )

    @api.multi
    @api.depends('picking_ids')
    def _compute_picking_state(self):
        for order in self:
            states = set()
            for picking in order.picking_ids:
                states.add(picking.state)
            if 'done' not in states:
                order.picking_state = 'unprocessed'
            elif len(states) == 1:
                order.picking_state = 'done'
            else:
                order.picking_state = 'partially'
