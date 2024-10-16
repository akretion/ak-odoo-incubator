# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import imghdr

from odoo import api, models

LIMIT = 500


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _generate_image_zipfile(self):
        prd_ids = self.env.context["active_ids"]
        if prd_ids:
            if len(prd_ids) > LIMIT:
                raise ValueError(f"Too many selected products : limit = {LIMIT}")
            return (
                self.env["zip.product.image"]
                .create({})
                ._get_zip_product_images(self.browse(prd_ids))
            )

    def _product_image_data(self):
        self.ensure_one()
        if "fs_product_multi_image" in self.env.registry._init_modules:
            # Here fs_product_multi_image is installed
            if self.image:
                return (base64.b64encode(self.image.getvalue()), self.image.extension)
            return (False, False)
        image_data = base64.b64decode(self.image_1920)
        image_type = imghdr.what(None, h=image_data)
        return (self.image_1920 or False, f".{image_type}")
