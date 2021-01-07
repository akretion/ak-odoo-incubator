# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_new_planned_date(self, delay):
        return fields.Datetime.now() + timedelta(days=delay)

    def _prepare_stock_moves(self, picking):
        ongoing_moves = self.move_ids.filtered(
            lambda m: m.state not in ("cancel", "done")
        )
        if not ongoing_moves:
            product = self.product_id
            delay = 0
            seller = product._select_seller(
                partner_id=self.order_id.partner_id, quantity=self.product_qty
            )
            delay = seller.delay or 0
            date_planned = self._get_new_planned_date(delay)
            self.write({"date_planned": date_planned})
        return super()._prepare_stock_moves(picking)
