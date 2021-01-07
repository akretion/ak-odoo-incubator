# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def update_delay_from_incoming_shipment(self):
        po_moves = self.filtered(lambda m: m.purchase_line_id)
        supplierinfos = self.env["product.supplierinfo"]
        for move in po_moves:
            product = move.product_id
            supplierinfos |= product._select_seller(
                partner_id=move.picking_id.partner_id,
                quantity=move.purchase_line_id.product_qty,
            )
        supplierinfos._update_delay()
