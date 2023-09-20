# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    required_certificat_ids = fields.Many2many(
        comodel_name="certificat.typology",
        string="Requested certificats",
    )

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        for template, vals in zip(templates, vals_list):
            if "required_certificat_ids" in vals:
                template.product_variant_ids.write(
                    {"required_certificat_ids": vals["required_certificat_ids"]}
                )
        return templates

    def write(self, vals):
        res = super().write(vals)
        if "required_certificat_ids" in vals:
            self.product_variant_ids.write(
                {"required_certificat_ids": vals["required_certificat_ids"]}
            )
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    required_certificat_ids = fields.Many2many(
        comodel_name="certificat.typology",
        string="Requested certificats",
    )
