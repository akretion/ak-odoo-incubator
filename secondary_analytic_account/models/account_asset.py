from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    second_analytic_account_id = fields.Many2one(
        comodel_name="secondary.account.analytic.account",
        string="Second Analytic account",
        compute="_compute_secondary_account_analytic_id",
        readonly=False,
        store=True,
    )

    @api.depends("profile_id")
    def _compute_secondary_account_analytic_id(self):
        for asset in self:
            asset.second_analytic_account_id = (
                asset.profile_id.second_account_analytic_id
            )
