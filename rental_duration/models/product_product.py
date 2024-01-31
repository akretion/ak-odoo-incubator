# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Here we avoid check uom as days.
    # TODO: adapt the code in sale_rental module after
    # its migration, it will be cleaner than this copied code.
    @api.constrains("rented_product_id", "must_have_dates", "type", "must_have_duration")
    def _check_rental(self):
        products = self.filtered(
            lambda prod: prod.must_have_duration and \
                         prod.product_tmpl_id.rented_product_tmpl_id
        )
        for product in products:
            if product.rented_product_id:
                if product.type != "service":
                    raise ValidationError(
                        _("The rental product '{}' must be of type 'Service'.").format(
                            product.name
                        )
                    )
                if not product.must_have_dates:
                    raise ValidationError(
                        _(
                            "The rental product '{}' must have the option "
                            "'Must Have Start and End Dates' checked."
                        ).format(product.name)
                    )
        return super(ProductProduct, self - products)._check_rental()
