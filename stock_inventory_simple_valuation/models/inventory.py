# coding: utf-8
# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    explanation = fields.Text(
        help="Explain computation method for each product")


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    value = fields.Float(compute='_compute_value', string="Value")

    @api.one
    def _compute_value(self):
        # infos supplier
        # centrale d'achat
        #
        self.value = 1
        # if len(self.product_id.seller_ids) < 1:  # Product has no sellers
        #     self.value = round(
        #         float(self.product_id.standard_price * self.product_qty), 2)
        # else:  # has sellers
        #     suppliers = self.product_id.seller_ids.sorted(
        #         key=lambda r: r.sequence)
        #     right_supplier = suppliers[0]
        #     self.value = round(
        #         float(right_supplier.price * self.product_qty), 2)
