from odoo import fields, models


class SecondaryAccountAnalyticAccount(models.Model):
    _name = "secondary.account.analytic.account"

    name = fields.Char(
        string="Secondary Analytic Account", index=True, required=True, tracking=True
    )
    code = fields.Char(string="Reference", index=True, tracking=True, size=15)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
