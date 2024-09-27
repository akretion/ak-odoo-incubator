# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    product_ids = fields.Many2many(
        domain="[('type', '=', 'product'), ('to_inventory', '=', True),"
        " '|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )

    def action_open_inventory_lines(self):
        action = super().action_open_inventory_lines()
        action["domain"].append(("product_id.to_inventory", "=", True))
        return action

    def _get_quantities(self):
        return super(
            StockInventory, self.with_context(stock_inventory=True)
        )._get_quantities()
