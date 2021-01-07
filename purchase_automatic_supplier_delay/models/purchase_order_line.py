# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _get_new_planned_date(self, delay):
        return fields.Datetime.now() + timedelta(days=delay)

    @api.multi
    def _prepare_stock_moves(self, picking):
        ongoing_moves = self.move_ids.filtered(
            lambda m: m.state not in ("cancel", "done")
        )
        if not ongoing_moves:
            product = self.product_id
            supplier = picking.partner_id
            delay = 0
            for supplier_info in product.seller_ids:
                if supplier_info.name.id == supplier.id:
                    delay = supplier_info.delay
                    break
            delay = delay or supplier.delivery_delay or 0
            date_planned = self._get_new_planned_date(delay)
            self.write({"date_planned": date_planned})
        return super()._prepare_stock_moves(picking)
