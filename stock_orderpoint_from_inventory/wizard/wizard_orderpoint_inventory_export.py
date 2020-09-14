# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizardOrderpointInventoryExport(models.TransientModel):
    _inherit = "wizard.orderpoint.matrix.export"
    _name = "wizard.orderpoint.inventory.export"
    _description = "Wizard Orderpoint Inventory Export"

    dummy_origin = fields.Many2one("wizard.orderpoint.matrix.export")
    inventory_id = fields.Many2one("stock.inventory", required=True)

    def _compute_product_ids(self):
        self.product_ids = self.inventory_id.line_ids.mapped("product_id")

    def _generate_orderpoint_vals(self, product, warehouse):
        line = self.inventory_id.line_ids.filtered(lambda r: r.product_id == product)
        ratio_min = float(
            self.env["ir.config_parameter"].get_param(
                "orderpoint_initialize_from_inventory_ratio_min", default=0.5
            )
        )
        ratio_max = float(
            self.env["ir.config_parameter"].get_param(
                "orderpoint_initialize_from_inventory_ratio_max", default=1.0
            )
        )
        lead_days = float(
            self.env["ir.config_parameter"].get_param(
                "orderpoint_initialize_from_inventory_lead_days", default=1.0
            )
        )
        current_qty = line.product_qty
        return [
            current_qty,
            current_qty * ratio_min,
            current_qty * ratio_max,
            lead_days,
            1,
        ]

    def button_export_refresh_result(self):
        result = super().button_export_refresh_result()
        result.update({"res_model": "wizard.orderpoint.inventory.export"})
        return result
