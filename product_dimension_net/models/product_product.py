# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_length_net = fields.Float(
        "Longueur (net)", help="Longueur de l'article en dehors de son emballage"
    )
    product_height_net = fields.Float(
        "Hauteur (net)", help="Hauteur de l'article en dehors de son emballage"
    )
    product_width_net = fields.Float(
        "Largeur (net)", help="Largeur de l'article en dehors de son emballage"
    )
    volume_net = fields.Float(
        string="Volume (net)",
        help="Volume de l'article en dehors de son emballage",
        compute="_compute_net_dimensions",
        readonly=False,
        store=True,
    )
    net_dimension = fields.Char(
        compute="_compute_net_dimensions",
        store=True,
        readonly=True,
        help="String representing dimensions",
    )

    @api.depends(
        "product_length_net",
        "product_height_net",
        "product_width_net",
        "dimensional_uom_id",
    )
    def _compute_net_dimensions(self):
        template_obj = self.env["product.template"]
        for product in self:
            product.volume = template_obj._calc_volume(
                product.product_length_net,
                product.product_height_net,
                product.product_width_net,
                product.dimensional_uom_id,
            )
            product.net_dimension = (
                f"L{round(product.product_length_net)} "
                f"x l{round(product.product_width_net)} "
                f"x H{round(product.product_height_net)}"
            )
