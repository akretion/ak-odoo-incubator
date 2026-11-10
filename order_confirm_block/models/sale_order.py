from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _confirmation_error_message(self):
        return self.env._(
            "Sale order confirmation is disabled on this database "
            "(module order_confirm_block)."
        )
