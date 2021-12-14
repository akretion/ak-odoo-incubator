# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    product_attribute_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Attribute Values",
        help="Specify values if this rule only applies to this product "
        "attribute values. Keep empty otherwise.",
    )
    allowed_attribute_value_ids = fields.Many2many(
        "product.attribute.value", compute="_compute_allowed_attribute_value_ids"
    )

    def _compute_allowed_attribute_value_ids(self):
        for item in self:
            allowed_attribute_values = self.env["product.attribute.value"]
            if item.applied_on == "1_product" and item.product_tmpl_id:
                ptav_ids = (
                    item.product_tmpl_id.product_variant_ids.product_template_attribute_value_ids
                )
                allowed_attribute_values = ptav_ids.product_attribute_value_id
            if item.applied_on == "2_product_category" and item.categ_id:
                product_templates = self.env["product.template"].search(
                    [("categ_id", "child_of", item.categ_id.id)]
                )
                ptav_ids = (
                    product_templates.product_variant_ids.product_template_attribute_value_ids
                )
                allowed_attribute_values = ptav_ids.product_attribute_value_id
            if item.applied_on == "3_global":
                product_templates = self.env["product.template"].search([])
                ptav_ids = (
                    product_templates.product_variant_ids.product_template_attribute_value_ids
                )
                allowed_attribute_values = ptav_ids.product_attribute_value_id
            item.allowed_attribute_value_ids = allowed_attribute_values

    @api.onchange("applied_on")
    def _onchange_applied_on(self):
        for item in self:
            item.product_attribute_value_ids = self.env["product.attribute.value"]
            item._compute_allowed_attribute_value_ids()

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self):
        super()._onchange_product_tmpl_id()
        for item in self:
            item._compute_allowed_attribute_value_ids()

    @api.onchange("categ_id")
    def _onchange_categ_id(self):
        for item in self:
            item._compute_allowed_attribute_value_ids()

    @api.depends(
        "applied_on",
        "categ_id",
        "product_tmpl_id",
        "product_id",
        "compute_price",
        "fixed_price",
        "pricelist_id",
        "percent_price",
        "price_discount",
        "price_surcharge",
        "product_attribute_value_ids",
    )
    def _get_pricelist_item_name_price(self):
        res = super()._get_pricelist_item_name_price()
        for item in self:
            list_value_name = []
            for attribute_value in item.product_attribute_value_ids:
                list_value_name.append(attribute_value.name)
            if list_value_name:
                item.name = item.name + " (" + _(", ".join(list_value_name)) + ")"
        return res

    def _match(self, product, qty_in_product_uom, is_product_template):
        res = super()._match(product, qty_in_product_uom, is_product_template)
        attribute_id = False
        item_attribute_values = {}
        for attribute_value in self.product_attribute_value_ids.sorted(
            key=lambda v: v.attribute_id
        ):
            if attribute_id != attribute_value.attribute_id.id:
                attribute_id = attribute_value.attribute_id.id
                item_attribute_values[
                    attribute_id
                ] = self.product_attribute_value_ids.filtered(
                    lambda v: v.attribute_id.id == attribute_id
                ).ids

        if item_attribute_values:
            item_attributes = list(item_attribute_values.keys())
            for ptav in product.product_template_attribute_value_ids:
                if ptav.attribute_id.id not in item_attributes:
                    return False
                else:
                    if (
                        ptav.product_attribute_value_id.id
                        not in item_attribute_values.get(ptav.attribute_id.id)
                    ):
                        return False
        return res
