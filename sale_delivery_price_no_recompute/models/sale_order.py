# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_open_delivery_wizard(self):
        action = super().action_open_delivery_wizard()
        delivery_line = self.env["sale.order.line"].search(
            [("order_id", "in", self.ids), ("is_delivery", "=", True)], limit=1
        )
        action["context"].update(
            {
                "default_display_price": delivery_line.price_unit or 0.0,
                "default_delivery_price": delivery_line.price_unit or 0.0,
            }
        )
        return action
