# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _compute_is_quantity_done_editable(self):
        super()._compute_is_quantity_done_editable()
        for move in self:
            if move.state in ["done", "cancel"]:
                move.is_quantity_done_editable = False

    @api.depends("sale_line_id", "picking_id")
    def _compute_is_initial_demand_editable(self):
        super()._compute_is_initial_demand_editable()
        for move in self:
            if (
                move.sale_line_id and move.picking_type_id.code == "outgoing"
            ) or move.state in ["done", "cancel"]:
                move.is_initial_demand_editable = False

    def _quantity_done_set(self):
        for move in self:
            if move.state in ["done", "cancel"]:
                raise UserError(
                    _(
                        "You cannot modify the done quantity of a move that "
                        "is done or cancelled."
                    )
                )
        return super()._quantity_done_set()
