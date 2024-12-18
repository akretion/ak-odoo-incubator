from odoo import models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    def write(self, vals):
        res = super().write(vals)
        if "price" in vals or "discount" in vals:
            for rec in self:
                update_cost_from_main_price(rec)
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        res = super().write(vals)
        if "main_seller_id" in vals:
            for product in self:
                update_cost_from_main_price(product.main_seller_id, product)
        return res


def update_cost_from_main_price(suppinfo, product=None):
    if not product:
        product = suppinfo.product_id or suppinfo.product_tmpl_id.product_variant_id
    if product and product.main_seller_id == suppinfo:
        product.standard_price = suppinfo.price * (1 - suppinfo.discount / 100)
