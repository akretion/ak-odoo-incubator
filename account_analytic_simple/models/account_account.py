# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    analytic_simple_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Policy for analytic account simple",
        default="optional",
        help=(
            "Sets the policy for analytic accounts.\n"
            "If you select:\n"
            "- Optional: The accountant is free to put an analytic account "
            "on an account move line with this type of account.\n"
            "- Always: The accountant will get an error message if "
            "there is no analytic account.\n"
            "- Posted moves: The accountant will get an error message if no "
            "analytic account is defined when the move is posted.\n"
            "- Never: The accountant will get an error message if an analytic "
            "account is present.\n\n"
        ),
    )

    def _get_analytic_simple_policy(self):
        """Extension point to obtain simple analytic policy for an account"""
        self.ensure_one()
        return self.analytic_simple_policy
