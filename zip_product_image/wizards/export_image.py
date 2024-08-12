# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
import zipfile
from io import BytesIO

from odoo import _, exceptions, fields, models

logger = logging.getLogger(__name__)


class ZipProductImage(models.TransientModel):
    _name = "zip.product.image"
    _description = "Wizard to generate a zip images of selected products"

    zipfile = fields.Binary(string="Images Archive")
    name_zipfile = fields.Char()

    def _get_zip_product_images(self, products):
        """Generate a zip file with the images of the products."""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for prd in products:
                img_data, extension = prd._product_image_data()
                if img_data:
                    img_data = base64.b64decode(img_data)
                    name = ""
                    for field in self._product_field_names():
                        name = name or prd[field]
                    zip_file.writestr(
                        f"{name}{extension}", img_data
                    )
                else:
                    logger.warning(f"Product {prd.display_name} has no image")
        if zip_file.filelist:
            self.zipfile = base64.b64encode(zip_buffer.getvalue())
            self.name_zipfile = "product_images.zip"
            action = self.get_formview_action()
            action["target"] = "new"
            return action
        raise exceptions.UserError(_("No image for this product selection"))

    def _product_field_names(self):
        return ["barcode", "default_code", "name"]
