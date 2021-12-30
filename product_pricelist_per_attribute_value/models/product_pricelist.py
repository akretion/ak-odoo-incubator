# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools

from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule_get_items(
        self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
    ):
        items = super()._compute_price_rule_get_items(
            products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
        )
        # Reapply sort _order of the class
        return self.env["product.pricelist.item"].search([("id", "in", items.ids)])


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    _order = (
        "applied_on, attribute_value_restricted desc, min_quantity desc,"
        "categ_id desc, id desc"
    )

    attribute_value_restricted = fields.Boolean(
        compute="_compute_attribute_value_restricted", store=True
    )
    product_attribute_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Attribute Values",
        help="Specify values if this rule only applies to this product "
        "attribute values. Keep empty otherwise.",
    )

    @api.depends("product_attribute_value_ids")
    def _compute_attribute_value_restricted(self):
        for record in self:
            record.attribute_value_restricted = bool(record.product_attribute_value_ids)

    @api.onchange("applied_on", "product_tmpl_id", "categ_id")
    def _onchange_attribute_value_domain(self):
        self.ensure_one()
        domain = []
        self.product_attribute_value_ids = None
        if self.applied_on == "1_product" and self.product_tmpl_id:
            values = self.product_tmpl_id.attribute_line_ids.value_ids
            domain = [("id", "in", values.ids)]
        elif self.applied_on == "2_product_category" and self.categ_id:
            product_templates = self.env["product.template"].search(
                [("categ_id", "child_of", self.categ_id.id)]
            )
            values = product_templates.attribute_line_ids.value_ids
            domain = [("id", "in", values.ids)]
        return {"domain": {"product_attribute_value_ids": domain}}

    @api.depends("product_attribute_value_ids.name")
    def _get_pricelist_item_name_price(self):
        res = super()._get_pricelist_item_name_price()
        for item in self:
            if item.product_attribute_value_ids:
                item.name += (
                    f" ({', '.join(item.product_attribute_value_ids.mapped('name'))})"
                )
        return res

    def _is_applicable_for(self, product, qty_in_product_uom):
        res = super()._is_applicable_for(product, qty_in_product_uom)
        if self.product_attribute_value_ids:
            ptav = product.product_template_attribute_value_ids
            attr2vals = {
                attribute: set(values)
                for attribute, values in itertools.groupby(
                    self.product_attribute_value_ids, lambda pav: pav.attribute_id
                )
            }
            for attribute in attr2vals:
                if attribute not in ptav.attribute_id:
                    return False
                elif not attr2vals[attribute] & set(ptav.product_attribute_value_id):
                    return False
        return res
