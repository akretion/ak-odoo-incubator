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
        return self.env["report"].get_action(
                self, 'stock_picking_wave_report.report_picking_wave')
