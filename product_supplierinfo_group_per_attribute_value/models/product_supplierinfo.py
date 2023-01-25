# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.depends("group_id.product_attribute_value_ids")
    def _compute_product_attribute_value_ids(self):
        for record in self:
            record.product_attribute_value_ids = (
                record.group_id.product_attribute_value_ids
            )

    def _none_writable_related_fields(self):
        return super()._none_writable_related_fields() + ["product_attribute_value_ids"]

    def _get_existing_group(self, field_mapping, vals):
        # Searching several value on m2m is considered by odoo as a "in"
        # and not a strict equal
        # so we need to remove the field "product_attribute_value_ids"
        # from the search and then filter on it
        mapping = [
            (field_supplierinfo, field_group)
            for field_supplierinfo, field_group in field_mapping
            if field_group != "product_attribute_value_ids"
        ]
        group = super()._get_existing_group(mapping, vals)
        if vals.get("product_attribute_value_ids"):
            ids = set(vals["product_attribute_value_ids"][0][2])
            return group.filtered(
                lambda s: set(s.product_attribute_value_ids.ids) == ids
            )
        return group

    def _fields_for_group_match(self):
        res = super()._fields_for_group_match()
        res["product_attribute_value_ids"] = "product_attribute_value_ids"
        return res
