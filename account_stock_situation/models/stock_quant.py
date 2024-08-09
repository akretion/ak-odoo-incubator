from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    warehouse_id = fields.Many2one(store=True, index=True)
