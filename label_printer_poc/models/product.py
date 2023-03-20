import logging

from odoo import models

_logger = logging.getLogger(__name__)

class Product(models.Model):
    name="product.product"
    _inherit = "product.product"

    def get_labels_zebra(self, print_data, with_price=False):
        zpl_data = []
        for product, quantity in print_data:
            report = self.env["ir.actions.report"]._get_report_from_name("stock.label_barcode_product_product_view")
            zpl_data.append((report._render_qweb_text([product.id])[0], quantity))
        return zpl_data
