# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_length_net = fields.Float(
        related="product_variant_ids.product_length_net", readonly=False
    )
    product_height_net = fields.Float(
        related="product_variant_ids.product_height_net", readonly=False
    )
    product_width_net = fields.Float(
        related="product_variant_ids.product_width_net", readonly=False
    )
    volume_net = fields.Float(
        string="Volume (net)",
        compute="_compute_volume_net",
        readonly=False,
        store=True,
    )

    @api.depends(
        "product_length", "product_height", "product_width", "dimensional_uom_id"
    )
    def _compute_volume_net(self):
        for template in self:
            template.volume = template._calc_volume(
                template.product_length_net,
                template.product_height_net,
                template.product_width_net,
                template.dimensional_uom_id,
            )
