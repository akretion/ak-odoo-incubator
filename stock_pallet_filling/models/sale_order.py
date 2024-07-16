# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = ["sale.order", "pallet.filling.mixin"]
    _name = "sale.order"

    @api.depends(
        "order_line.product_uom_qty",
        "order_line.product_packaging_id",
        "order_line.product_packaging_id.package_type_id.volume",
    )
    def _compute_pallet_estimation(self):
        return super()._compute_pallet_estimation()

    @property
    def _pallet_line_fieldname(self):
        return "order_line"
