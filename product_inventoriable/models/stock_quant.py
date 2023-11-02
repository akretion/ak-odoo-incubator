# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        if self.env.context.get("stock_inventory", False):
            domain.append(("product_id.to_inventory", "=", True))
        return super().read_group(
            domain=domain,
            fields=fields,
            groupby=groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
