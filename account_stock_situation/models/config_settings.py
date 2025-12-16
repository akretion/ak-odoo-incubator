from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    valued_warehouse_ids = fields.Many2many(
        related="company_id.valued_warehouse_ids", readonly=False
    )
    cost_vs_purchase_threshold = fields.Integer(
        related="company_id.cost_vs_purchase_threshold", readonly=False, default=120
    )
    stock_journal_id = fields.Many2one(
        comodel_name="account.journal",
        readonly=False,
        related="company_id.stock_journal_id",
        domain=[("type", "=", "general")],
    )
    account_purchase_stock_id = fields.Many2one(
        comodel_name="account.account",
        readonly=False,
        related="company_id.account_purchase_stock_id",
    )
    account_stock_id = fields.Many2one(
        comodel_name="account.account",
        readonly=False,
        related="company_id.account_stock_id",
    )
    account_stock_help = fields.Text(compute="_compute_account_stock_help")

    def _compute_account_stock_help(self):
        for rec in self:
            name = ""
            if "l10n_fr" in self.env.registry._init_modules:
                name = "Compte de stock: '355...'"
                name += "Compte de stock d'achat: '603...'"
            rec.account_stock_help = name
