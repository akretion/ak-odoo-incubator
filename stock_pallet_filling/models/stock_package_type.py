# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackageType(models.Model):

    _inherit = "stock.package.type"

    volume = fields.Float(
        compute="_compute_volume", store=True, help="Volume en millimètres cube"
    )

    @api.depends("packaging_length", "width", "height")
    def _compute_volume(self):
        for rec in self:
            rec.volume = rec.packaging_length * rec.width * rec.height
