# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from os import path
from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase

PATH = path.dirname(__file__) + "/fixtures/"
import base64


class TestOrderpointImport(SavepointCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self.env.ref("stock.warehouse0")

    def _helper_import_excel(self, filepath):
        data = base64.b64encode(open(PATH + filepath, "rb").read())
        wizard = self.env["wizard.orderpoint.matrix.import"].create(
            {"file": data, "filename": "does not matter"}
        )
        wizard.button_import_excel()

    def test_delete(self):
        self._helper_import_excel("delete_wh1_product27_product11.xlsx")
        with self.assertRaises(ValueError) as e:
            self.env.ref("stock_orderpoint_impex_matrix.orderpoint_wh1_product11")
        self.assertIn("External ID not found in the system", e.exception.args[0])
        with self.assertRaises(ValueError) as e:
            self.env.ref("stock_orderpoint_impex_matrix.orderpoint_wh1_product27")
        self.assertIn("External ID not found in the system", e.exception.args[0])

    def test_update_orderpoint(self):
        self._helper_import_excel("update_wh1_product10_product11.xlsx")
        updated_vals_wh1_product10 = {
            "product_min_qty": 789,
            "product_max_qty": 963,
            "lead_days": 2,
            "qty_multiple": 3,
        }
        orderpoint_wh1_product10 = self.env.ref(
            "stock_orderpoint_impex_matrix.orderpoint_wh1_product10"
        )
        for key, val in updated_vals_wh1_product10.items():
            self.assertAlmostEqual(getattr(orderpoint_wh1_product10, key), val)
        orderpoint_wh1_product11 = self.env.ref(
            "stock_orderpoint_impex_matrix.orderpoint_wh1_product11"
        )
        updated_vals_wh1_product11 = {
            "product_min_qty": 654,
            "product_max_qty": 321,
            "lead_days": 9,
            "qty_multiple": 7,
        }
        for key, val in updated_vals_wh1_product11.items():
            self.assertAlmostEqual(getattr(orderpoint_wh1_product11, key), val)

    def test_create_orderpoint(self):
        self.env.ref(
            "stock.stock_warehouse_orderpoint_2"
        ).unlink()  # orderpoint for Flipover
        self._helper_import_excel("create_wh1_product20.xlsx")
        orderpoint = self.env["stock.warehouse.orderpoint"].search(
            [
                ("name", "=", "Flipover (YourCompany)"),
                ("warehouse_id", "=", self.warehouse.id),
            ]
        )
        self.assertTrue(orderpoint)
        expected_vals = {
            "product_min_qty": 654,
            "product_max_qty": 321,
            "lead_days": 9,
            "qty_multiple": 7,
        }
        for key, val in expected_vals.items():
            self.assertAlmostEqual(getattr(orderpoint, key), val)

    def test_bad_wh_name(self):
        with self.assertRaises(ValidationError) as e:
            self._helper_import_excel("bad_wh_name.xlsx")
        self.assertEqual(
            e.exception.name, _("Warehouse names should match to exactly one warehouse")
        )

    def test_bad_product_name(self):
        with self.assertRaises(ValidationError) as e:
            self._helper_import_excel("bad_product_name.xlsx")
        self.assertEqual(
            e.exception.name, _("Product names should match to exactly one product")
        )

    def test_bad_structure(self):
        with self.assertRaises(ValidationError) as e:
            self._helper_import_excel("bad_structure.xlsx")
        self.assertEqual(
            e.exception.name, _("Bad parity for columns, some were removed or added")
        )

    def test_incomplete_values(self):
        with self.assertRaises(ValidationError) as e:
            self._helper_import_excel("incomplete_values.xlsx")
        self.assertEqual(
            e.exception.name,
            _("For each warehouse, either fill all values or empty all values"),
        )
