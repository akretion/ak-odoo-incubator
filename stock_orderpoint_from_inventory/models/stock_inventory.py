# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def button_generate_orderpoint_export_xlsx(self):
        self.ensure_one()
        warehouse = self.env["stock.warehouse"].search(
            [("lot_stock_id", "=", self.location_id.id)]
        )
        if len(warehouse.ids) != 1:
            raise ValidationError(
                _(
                    "Warehouse configuration error. Stock locations per"
                    " warehouse should be set and mutually unique."
                )
            )
        vals = {"warehouse_ids": [(6, 0, warehouse.ids)], "inventory_id": self.id}
        wizard = self.env["wizard.orderpoint.inventory.export"].create(vals)
        return wizard.button_export_refresh_result()
