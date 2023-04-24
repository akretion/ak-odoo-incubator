from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    print_config_id = fields.Many2one(comodel_name="print.config")
