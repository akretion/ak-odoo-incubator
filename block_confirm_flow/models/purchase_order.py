# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        raise UserError(
            _(
                "Unable to validate Purchase Order,"
                "(blocked by module block_confirm_flow before production release)"
            )
        )
