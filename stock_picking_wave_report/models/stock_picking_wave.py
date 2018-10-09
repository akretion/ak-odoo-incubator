# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class StockPickingWave(models.Model):
    _inherit = "stock.picking.wave"


    @api.multi
    def print_picking(self):
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        return self.env.ref('stock_picking_wave_report.action_report_picking_wave').report_action(self)

