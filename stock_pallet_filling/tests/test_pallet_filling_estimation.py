# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPalletFillingEstimation(TransactionCase):
    def setUp(self):
        super().setUp()
        cpny = self.env.ref("base.main_company")
        self.prd_1 = self.env["product.product"].create(
            {
                "name": "PRD1",
                "default_code": "PRD1",
                "company_id": cpny.id,
            }
        )
        self.prd_2 = self.env["product.product"].create(
            {
                "name": "PRD2",
                "default_code": "PRD2",
                "company_id": cpny.id,
            }
        )
        self.pkg_type = self.env["stock.package.type"].create(
            {
                "name": "Test Package Type",
                "packaging_length": 1000,
                "width": 1000,
                "height": 1000,
            }
        )

        def get_pack_vals(product):
            return {
                "product_id": product.id,
                "name": "any",
                "qty": 50,
                "company_id": self.env.company.id,
                "package_type_id": self.pkg_type.id,
            }

        vals_list = [
            get_pack_vals(self.prd_2),
            get_pack_vals(self.prd_1),
        ]
        self.env["product.packaging"].create(vals_list)

        def get_line_vals(product):
            return {
                "name": product.name,
                "product_id": product.id,
                "product_packaging_qty": 20,
                "product_packaging_id": product.packaging_ids[0].id,
                "product_uom_qty": 1000,  # onchange not played
            }

        so_vals = {
            # gemini
            "partner_id": self.env.ref("base.res_partner_3").id,
            "order_line": [
                (0, 0, get_line_vals(self.prd_2)),
                (0, 0, get_line_vals(self.prd_1)),
            ],
        }
        self.so_gemi = self.env["sale.order"].create(so_vals)
        self.so_gemi.action_confirm()
        self.picking = self.so_gemi.picking_ids

    def test_calculate_pallet_filling(self):
        # 1000 units, 50 per pack => 20 packages per product => 20m3 per product
        # 40 m3 / 1.188 m3 = 34 pallets
        self.assertEqual(self.picking.pallet_estimation, 34)
        self.assertEqual(self.so_gemi.pallet_estimation, 34)

    def test_calculate_pallet_filling_error(self):
        # 20 m3 / 1.188 m3 = 17 pallets
        self.so_gemi.order_line[0].product_packaging_id = False
        self.assertEqual(self.picking.pallet_estimation, 17)
        self.assertTrue(self.picking.pallet_estimation_warning)
        self.assertEqual(self.so_gemi.pallet_estimation, 17)
        self.assertTrue(self.so_gemi.pallet_estimation_warning)
