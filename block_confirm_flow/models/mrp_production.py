# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_plan(self):
        raise UserError(
            _(
                "Unable to validate Work Order,"
                "(blocked by module block_confirm_flow before production release)"
            )
        )

    def action_confirm(self):
        raise UserError(
            _(
                "Unable to validate Manufacturing Orders,"
                "(blocked by module block_confirm_flow before production release)"
            )
        )
