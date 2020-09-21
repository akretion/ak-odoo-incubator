# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from io import BytesIO
from os import path

import openpyxl

from odoo.tests.common import SavepointCase

CELL_VALUE_EMPTY = None
PATH = path.dirname(__file__) + "/fixtures/"

PATH_DEBUGMODE = path.dirname(__file__)
DEBUGMODE_SAVE_EXPORT = True


class OrderpointExportCase(SavepointCase):
    def _get_resulting_sheet(self, warehouses):
        vals = {
            "warehouse_ids": [(6, 0, warehouses.ids)],
        }
        wizard = self.env["wizard.orderpoint.matrix.export"].create(vals)
        wizard.button_export_refresh_result()
        excel_file = BytesIO(base64.b64decode(wizard.file.decode("utf-8")))
        workbook = openpyxl.load_workbook(excel_file)
        if DEBUGMODE_SAVE_EXPORT:
            workbook.save(PATH_DEBUGMODE + self._testMethodName + ".xlsx")
        return workbook.worksheets[0]

    def _helper_check_expected_values(self, sheet, values, start_col=1, start_row=1):
        """ Checks given values are on the sheet """
        for idx_row, row_values in enumerate(values, start=start_row):
            for idx_cell, expected_val in enumerate(row_values, start=start_col):
                real_val = sheet.cell(row=idx_row, column=idx_cell).value
                self.assertEqual(real_val, expected_val)
