from odoo import models


class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"

    def _setup_move_line_data(self, depreciation_date, account, ml_type, move):
        move_line_data = super()._setup_move_line_data(
            depreciation_date, account, ml_type, move
        )
        move_line_data[
            "second_analytic_account_id"
        ] = self.asset_id.second_analytic_account_id.id
        return move_line_data
