# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SalePriceCustomerHistory(models.Model):
    _name = "sale.price.customer.history"
    _description = "Sale Price History per customer and product"

    partner_id = fields.Many2one("res.partner", required=True, index="btree")
    product_id = fields.Many2one("product.product", required=True, index="btree")
    price = fields.Float()
    date = fields.Date(required=True, index="btree")
    document_ref = fields.Char()
