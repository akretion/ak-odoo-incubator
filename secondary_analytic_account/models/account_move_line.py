from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    second_analytic_account_id = fields.Many2one(
        "secondary.account.analytic.account",
        string="Secondary Analytic Account",
        index=True,
        readonly=False,
        copy=True,
    )
