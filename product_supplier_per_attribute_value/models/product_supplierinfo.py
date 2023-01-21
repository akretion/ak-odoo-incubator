# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

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
        related="product_tmpl_id.attribute_line_ids.value_ids",
    )

    @api.depends("product_tmpl_id", "product_attribute_value_ids", "product_id")
    def _compute_product_definition_precision(self):
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
