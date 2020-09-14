# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from io import BytesIO
from os import path

import openpyxl

from odoo.tests.common import SavepointCase
from .common import OrderpointExportCase

CELL_VALUE_EMPTY = None
PATH = path.dirname(__file__) + "/fixtures/"

PATH_DEBUGMODE = path.dirname(__file__)
DEBUGMODE_SAVE_EXPORT = False


class TestOrderpointExport(OrderpointExportCase):
    def setUp(self):
        super().setUp()
        self.orderpoint_wh1 = self.env.ref(
            "stock_orderpoint_impex_matrix.orderpoint_wh1_product10"
        )
        self.orderpoint_wh2 = self.env.ref(
            "stock_orderpoint_impex_matrix.orderpoint_wh2_product10"
        )
        self.warehouse1 = self.env.ref("stock.warehouse0")
        self.warehouse2 = self.env.ref("stock_orderpoint_impex_matrix.demo_op_wh")

    def test_base_headers(self):
        """ Test headers structure: 2 warehouses """
        sheet = self._get_resulting_sheet(self.warehouse1 + self.warehouse2)
        expected_values = [
            [
                CELL_VALUE_EMPTY,
                "Entrepôt YourCompany",
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                "Entrepôt Demo OP WH",
            ],
            [
                "Article",
                "Quantité actuelle",
                "Quantité minimale",
                "Quantité maximale",
                "Délai fournisseur",
                "Multiple de quantité",
                "Quantité actuelle",
                "Quantité minimale",
                "Quantité maximale",
                "Délai fournisseur",
                "Multiple de quantité",
            ],
        ]
        self._helper_check_expected_values(sheet, expected_values)

    def test_data(self):
        """
        Check we get expected data for some of the demo orderpoints
        with varying situation (in wh1, not in wh2, reversed, and in both)
        """
        sheet = self._get_resulting_sheet(self.warehouse1 + self.warehouse2)
        expected_values = [
            [
                "Office Chair",
                0,
                3,
                5,
                1,
                1,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
            ],
            [
                "Office Lamp",
                0,
                5,
                10,
                1,
                1,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
            ],
            ["Cabinet with Doors", 8, 5.55, 6.66, 1, 1, 0, 11.11, 12.12, 1, 1],
            [
                "Conference Chair",
                26,
                1.11,
                2.22,
                1,
                1,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
                CELL_VALUE_EMPTY,
            ],
        ]
        self._helper_check_expected_values(sheet, expected_values, start_row=3)
