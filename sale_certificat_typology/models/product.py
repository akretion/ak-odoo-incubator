# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    required_certificat_ids = fields.Many2many(
        comodel_name="certificat.typology",
        string="Requested certificats",
    )
