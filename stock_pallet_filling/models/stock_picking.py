# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = ["stock.picking", "pallet.filling.mixin"]
    _name = "stock.picking"

    @api.depends(
        "move_ids.product_uom_qty",
        "move_ids.product_packaging_id",
        "move_ids.product_packaging_id.package_type_id.volume",
    )
    def _compute_pallet_estimation(self):
        return super()._compute_pallet_estimation()

    @property
    def _pallet_line_fieldname(self):
        return "move_ids"
