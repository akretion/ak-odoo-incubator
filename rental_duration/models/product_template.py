# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    must_have_duration = fields.Boolean(
        string="Must Have Duration",
        default=False,
        )

    @api.model_create_multi
    def create(self, values):
        template = super().create(values)
        if self.env.context.get("copy_for_rental") and self.env.company.rental_duration:
            template.uom_id = self.env.company.rental_uom_id.id
            template.must_have_duration = True
        return template

