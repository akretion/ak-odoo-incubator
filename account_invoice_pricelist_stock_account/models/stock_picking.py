# -*- coding: utf-8 -*-
# © 2018 Akretion <https://www.akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        """Set pricelist from purchase order if set on picking."""
        inv_vals = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move
        )
        if move.purchase_line_id.order_id.pricelist_id:
            inv_vals.update({
                'pricelist_id': move.purchase_line_id.order_id.pricelist_id.id,
            })
        return inv_vals
