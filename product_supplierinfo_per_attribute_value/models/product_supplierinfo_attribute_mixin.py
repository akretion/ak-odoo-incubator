# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductSupplierinfoAttributeMixin(models.AbstractModel):
    _name = "product.supplierinfo.attr.mixin"
    _description = "Product Supplierinfo Attribute Mixin"

    product_tmpl_id = fields.Many2one("product.template")
    product_definition_precision = fields.Integer(
        compute="_compute_product_definition_precision", store=True
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
    allowed_attribute_value_ids = fields.Many2many(
        "product.attribute.value",
        compute="_compute_allowed_attribute_value_ids",
    )

    @api.depends("product_tmpl_id.attribute_line_ids.value_ids")
    def _compute_allowed_attribute_value_ids(self):
        for record in self:
            record.allowed_attribute_value_ids = (
                record.product_tmpl_id.attribute_line_ids.value_ids
            )

    @api.depends("product_tmpl_id", "product_attribute_value_ids", "product_id")
    def _compute_product_definition_precision(self):
        # Product definition have kind of the same behaviour as we have on
        # the pricelist item take the price from
        # specific rule (on the product)
        # then based on the attribute
        # and if nothing match use the generic rule of the supplier
        # Native odoo just take the best price so if you define a price
        # on a variant and on the template if the price on the template
        # is the less expensive it will always take it
        for record in self:
            if record.product_id:
                record.product_definition_precision = 9999
            elif record.product_attribute_value_ids:
                record.product_definition_precision = len(
                    record.product_attribute_value_ids.attribute_id
                )
            else:
                record.product_definition_precision = 0

    @api.depends("product_attribute_value_ids")
    def _compute_attribute_value_restricted(self):
        for record in self:
            record.attribute_value_restricted = bool(record.product_attribute_value_ids)

    @api.depends("product_tmpl_id", "product_id")
    def _compute_product_attribute_value_ids(self):
        for record in self:
            if record.product_id:
                record.product_attribute_value_ids = None
            elif record.product_attribute_value_ids:
                record.product_attribute_value_ids &= record.allowed_attribute_value_ids
