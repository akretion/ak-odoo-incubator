from odoo import fields, models


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"

    second_account_analytic_id = fields.Many2one(
        comodel_name="secondary.account.analytic.account",
        string="Second Analytic account",
    )
