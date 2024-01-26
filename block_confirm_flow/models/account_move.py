# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        raise UserError(
            _(
                "Unable to validate Account move,"
                "(blocked by module block_confirm_flow before production release)"
            )
        )
