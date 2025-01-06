import logging

from odoo import fields, models

logger = logging.getLogger(__name__)


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    def write(self, vals):
        res = super().write(vals)
        if "price" in vals or "discount" in vals:
            for rec in self:
                update_cost_from_main_price(rec)
        return res

    def _update_standard_price(self):
        """Only called from shell
        env['product.supplierinfo']._update_standard_price()
        """
        for prd in self.search([]).mapped("product_id"):
            if prd.standard_price != prd.main_seller_id.price * (
                1 - prd.main_seller_id.discount / 100
            ):
                previous = prd.standard_price
                update_cost_from_main_price(prd.main_seller_id)
                logger.info(
                    "> %s %s std price, previous %s"
                    % (prd.standard_price, prd.default_code, previous)
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(tracking=10)

    def write(self, vals):
        res = super().write(vals)
        if "main_seller_id" in vals and "standard_price" not in vals:
            for product in self:
                if product.main_seller_id:
                    update_cost_from_main_price(product.main_seller_id, product)
        return res

    def _update_snjb_standard_price(self):
        "env['product.product']._update_snjb_standard_price()"
        def get_products_with_zero_standard_price():
            prd_ids = []
            for prd in self.search([("standard_price", "=", 0)]):
                sell = prd.main_seller_id
                if sell and sell.price > 0:
                    prd_ids.append(prd.id)
            return self.browse(prd_ids)

        for prd in get_products_with_zero_standard_price():
            update_cost_from_main_price(prd.main_seller_id, prd)
            logger.info(f"\n > Updated price {prd.standard_price} from {prd.name}")
        missing = get_products_with_zero_standard_price()
        if missing:
            logger.info(f"\n>> Missing {missing}")


def update_cost_from_main_price(suppinfo, product=None):
    if not product:
        product = suppinfo.product_id or suppinfo.product_tmpl_id.product_variant_id
    if product and product.main_seller_id == suppinfo:
        product.standard_price = suppinfo.price * (1 - suppinfo.discount / 100)
