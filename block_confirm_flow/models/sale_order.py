# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        raise UserError(
            _(
                "Unable to validate Sale Order,"
                "(blocked by module block_confirm_flow before production release)"
            )
        )
