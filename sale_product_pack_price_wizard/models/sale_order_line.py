# Copyright 2023 Akretion - Raphaël Valyi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_pack_line = fields.Boolean(compute="_compute_is_pack_line")

    @api.depends("product_id")
    def _compute_is_pack_line(self):
        for line in self:
            line.is_pack_line = line.product_id.pack_ok or line.pack_parent_line_id
