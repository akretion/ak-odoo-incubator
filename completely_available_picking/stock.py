# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_ready = fields.Datetime(
        string='Ready', compute='_compute_picking_ready', store=True,
        help="Date when picking becomes 'Ready to transfert'")

    @api.depends('state')
    @api.multi
    def _compute_picking_ready(self):
        for rec in self:
            if rec.state == 'assigned':
                rec.picking_ready = fields.datetime.now()
