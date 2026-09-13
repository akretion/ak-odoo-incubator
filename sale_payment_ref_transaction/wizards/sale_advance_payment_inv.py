# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env["sale.order"].browse(self._context.get("active_ids", []))
        sale_orders.filtered(
            lambda so: not so.reference
        )._update_payment_ref_from_transaction()
        return super().create_invoices()
