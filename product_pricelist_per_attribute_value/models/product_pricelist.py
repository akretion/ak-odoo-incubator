# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools
import json

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
        compute="_compute_product_attribute_value_ids",
        readonly=False,
        store=True,
    )
    product_attribute_value_domain = fields.Char(
        compute="_compute_product_attribute_value_domain",
    )

    @api.depends("product_attribute_value_ids")
    def _compute_attribute_value_restricted(self):
        for record in self:
            record.attribute_value_restricted = bool(record.product_attribute_value_ids)

    @api.depends("applied_on", "product_tmpl_id", "categ_id")
    def _compute_product_attribute_value_domain(self):
        for record in self:
            if record.applied_on == "1_product" and record.product_tmpl_id:
                domain = [
                    (
                        "id",
                        "in",
                        record.product_tmpl_id.attribute_line_ids.value_ids.ids,
                    )
                ]
            elif record.applied_on == "2_product_category" and record.categ_id:
                product_templates = record.env["product.template"].search(
                    [("categ_id", "child_of", record.categ_id.id)]
                )
                domain = [
                    ("id", "in", product_templates.attribute_line_ids.value_ids.ids)
                ]
            else:
                domain = []
            record.product_attribute_value_domain = json.dumps(domain)

    @api.depends("applied_on", "product_tmpl_id", "categ_id")
    def _compute_product_attribute_value_ids(self):
        for record in self:
            if record.applied_on == "0_product_variant":
                record.product_attribute_value_ids = None
            elif record.product_attribute_value_ids:
                record.product_attribute_value_ids = (
                    record.product_attribute_value_ids.filtered_domain(
                        json.loads(record.product_attribute_value_domain)
                    )
                )

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
