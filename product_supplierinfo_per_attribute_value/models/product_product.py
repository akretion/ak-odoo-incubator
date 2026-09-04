# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import itertools

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _seller_matches_criteria(
        self, seller, partner_id=False, quantity=0.0, date=None, uom_id=False
    ):
        if not self._seller_matches_attributes(seller):
            return False
        return super()._seller_matches_criteria(
            seller, partner_id=partner_id, quantity=quantity, date=date, uom_id=uom_id
        )

    def _seller_matches_attributes(self, seller):
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
        return True

    def _get_filtered_sellers(
        self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False
    ):
        sellers = super()._get_filtered_sellers(
            partner_id=partner_id,
            quantity=quantity,
            date=date,
            uom_id=uom_id,
            params=params,
        )
        res = self.env["product.supplierinfo"]
        for seller in sellers:
            if res:
                current_precision = min(res.mapped("product_definition_precision"))
                if seller.product_definition_precision < current_precision:
                    continue
            res |= seller
        return res

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
