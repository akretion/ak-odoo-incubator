# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import itertools

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _is_valid_seller(self, seller, partner, quantity, date, uom, valid_sellers):
        if valid_sellers:
            # If sellers have been already selected we can only search for a better
            # matching rule so a seller with a bigger product_definition_precision
            current_precision = min(
                valid_sellers.mapped("product_definition_precision")
            )
            if seller.product_definition_precision < current_precision:
                return False
        if seller.product_attribute_value_ids:
            ptav = self.product_template_attribute_value_ids
            attr2vals = {
                attribute: set(values)
                for attribute, values in itertools.groupby(
                    seller.product_attribute_value_ids, lambda pav: pav.attribute_id
                )
            }
            for attribute in attr2vals:
                if attribute not in ptav.attribute_id:
                    return False
                elif not attr2vals[attribute] & set(ptav.product_attribute_value_id):
                    return False
        return super()._is_valid_seller(
            seller, partner, quantity, date, uom, valid_sellers
        )

    def _prepare_sellers(self, params=False):
        return (
            super()
            ._prepare_sellers(params=params)
            .sorted(
                lambda s: (
                    s.sequence,
                    -s.product_definition_precision,
                    -s.min_qty,
                    s.price,
                    s.id,
                )
            )
        )
