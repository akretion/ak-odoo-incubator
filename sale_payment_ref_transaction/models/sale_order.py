# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_payment_ref_from_transaction(self):
        for so in self:
            valid_transactions = so.transaction_ids.filtered(
                lambda so: so.state in ("draft", "pending", "authorized", "done")
            )
            if len(valid_transactions) == 1 and not so.reference:
                so.write({"reference": valid_transactions.reference})
