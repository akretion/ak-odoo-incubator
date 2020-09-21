# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from io import BytesIO

import openpyxl

from odoo.addons.stock_orderpoint_impex_matrix.tests.common import (
    OrderpointExportCase,
    DEBUGMODE_SAVE_EXPORT,
    PATH_DEBUGMODE,
)


class TestStockOrderpointInventory(OrderpointExportCase):
    def _get_resulting_sheet(self, warehouse, inventory):
        vals = {
            "warehouse_ids": [(6, 0, warehouse.ids)],
            "inventory_id": self.inventory.id,
        }
        wizard = self.env["wizard.orderpoint.inventory.export"].create(vals)
        wizard.button_export_refresh_result()
        excel_file = BytesIO(base64.b64decode(wizard.file.decode("utf-8")))
        workbook = openpyxl.load_workbook(excel_file)
        if DEBUGMODE_SAVE_EXPORT:
            workbook.save(PATH_DEBUGMODE + self._testMethodName + ".xlsx")
        return workbook.worksheets[0]

    def setUp(self):
        super().setUp()
        self.inventory = self.env.ref("stock.stock_inventory_0")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.env.ref("stock.stock_location_stock")
        self.inventory_line = self.env.ref("stock.stock_inventory_line_3")
        self.inventory_line_2 = self.env.ref("stock.stock_inventory_line_2")
        self.inventory_line_product = self.env.ref("product.product_product_6")
        self.inventory_line_2_product = self.env.ref("product.product_product_7")
        lines_to_delete = self.inventory.line_ids.filtered(
            lambda r: r.id not in [self.inventory_line.id, self.inventory_line_2.id]
        )
        lines_to_delete.unlink()

    def test_demo_inventory(self):
        sheet = self._get_resulting_sheet(self.warehouse, self.inventory)
        vals = [
            ["Large Cabinet", 1, 7, 500, 250, 500],
            ["Storage Box", 1, 7, 18, 9, 18],
        ]
        self._helper_check_expected_values(sheet, vals, start_row=3)
