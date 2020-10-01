# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from io import BytesIO

import openpyxl

from odoo.addons.stock_orderpoint_impex_matrix.tests.common import (
    DEBUGMODE_SAVE_EXPORT,
    PATH_DEBUGMODE,
    OrderpointExportCase,
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

    def test_demo_inventory(self):
        sheet = self._get_resulting_sheet(self.warehouse, self.inventory)
        vals = [
            ["E-COM07", "Large Cabinet", 500, 250, 500, 7, 1],
            ["E-COM08", "Storage Box", 18, 9, 18, 7, 1],
        ]
        self._helper_check_expected_values(sheet, vals, start_row=3)

    def test_demo_inventory_multiple_lines_for_one_product(self):
        stock_location_shelf2 = self.env.ref("stock.stock_location_14")
        self.env.ref("stock.stock_inventory_line_3").copy(
            {"location_id": stock_location_shelf2.id}
        )
        sheet = self._get_resulting_sheet(self.warehouse, self.inventory)
        vals = [
            ["E-COM07", "Large Cabinet", 1000, 500, 1000, 7, 1],
            ["E-COM08", "Storage Box", 18, 9, 18, 7, 1],
        ]
        self._helper_check_expected_values(sheet, vals, start_row=3)
