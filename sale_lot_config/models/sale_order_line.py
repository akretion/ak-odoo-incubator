# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["product.configuration.mixin", "sale.order.line"]

    def _prepare_vals_lot_number(self, index_lot):
        res = super()._prepare_vals_lot_number(index_lot)
        res["config"] = self.config
        return res
