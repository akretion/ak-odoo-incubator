from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _confirmation_error_message(self):
        return self.env._(
            "Purchase order confirmation is disabled on this database "
            "(module order_confirm_block)."
        )
