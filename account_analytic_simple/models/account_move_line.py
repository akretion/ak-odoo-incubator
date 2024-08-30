# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", index="btree"
    )

    def _check_analytic_simple_required_msg(self):
        self.ensure_one()
        company_cur = self.company_currency_id
        if company_cur.is_zero(self.debit) and company_cur.is_zero(self.credit):
            return None
        analytic_policy = self.account_id._get_analytic_simple_policy()
        if analytic_policy == "always" and not self.analytic_account_id:
            return _(
                "Analytic policy is set to 'Always' with account "
                "'%(account)s' but the analytic account is missing in "
                "the account move line with label '%(move)s'."
            ) % {
                "account": self.account_id.display_name,
                "move": self.name or "",
            }
        elif analytic_policy == "never" and (self.analytic_account_id):
            analytic_account = self.analytic_account_id
            return _(
                "Analytic policy is set to 'Never' with account "
                "'%(account)s' but the account move line with label '%(move)s' "
                "has an analytic account '%(analytic_account)s'."
            ) % {
                "account": self.account_id.display_name,
                "move": self.name or "",
                "analytic_account": analytic_account.name,
            }
        elif (
            analytic_policy == "posted"
            and not self.analytic_account_id
            and self.move_id.state == "posted"
        ):
            return _(
                "Analytic policy is set to 'Posted moves' with "
                "account '%(account)s' but the analytic account is missing "
                "in the account move line with label '%(move)s'."
            ) % {
                "account": self.account_id.display_name,
                "move": self.name or "",
            }
        return None

    @api.constrains("analytic_account_id", "account_id", "debit", "credit")
    def _check_analytic_simple_required(self):
        for rec in self:
            message = rec._check_analytic_simple_required_msg()
            if message:
                raise exceptions.ValidationError(message)
