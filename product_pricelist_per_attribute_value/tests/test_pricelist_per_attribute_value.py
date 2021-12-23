# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestPriceListPerAttributeValue(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ==== Product Attribute Values ====
        cls.pav_2 = cls.env.ref("product.product_attribute_value_2")
        cls.pav_3 = cls.env.ref("product.product_attribute_value_3")
        cls.pav_4 = cls.env.ref("product.product_attribute_value_4")
        # ==== Pricelist ====
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Pricelist 1"})
        # ==== Products ====
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.variant_1 = cls.env.ref("product.product_product_4c")
        cls.variant_2 = cls.env.ref("product.product_product_4d")
        # ==== Partners ====
        cls.partner = cls.env.ref("base.res_partner_1")

    def test_pricelist_item_name(self):
        pricelist_item_product = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 45.0,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            self.pav_2.id,
                            self.pav_3.id,
                        ],
                    )
                ],
            }
        )

        self.assertEqual(
            pricelist_item_product.name,
            "Product: Customizable Desk (CONFIG) (Aluminium, White)",
        )

    def test_leg_aluminum(self):
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 45.0,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            self.pav_2.id,
                        ],
                    )
                ],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_1, 1, self.partner, date=False, uom_id=self.variant_1.uom_id.id
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_2, 1, self.partner, date=False, uom_id=self.variant_2.uom_id.id
        )
        self.assertEqual(res1[0], 45.0)
        self.assertEqual(res2[0], 45.0)

    def test_leg_aluminum_white(self):
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 45.0,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            self.pav_2.id,
                            self.pav_3.id,
                        ],
                    )
                ],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_1, 1, self.partner, date=False, uom_id=self.variant_1.uom_id.id
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_2, 1, self.partner, date=False, uom_id=self.variant_2.uom_id.id
        )
        self.assertEqual(res1[0], 45.0)
        self.assertEqual(res2[0], 800.4)

    def test_color_white_and_black(self):
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 35.0,
                "applied_on": "2_product_category",
                "categ_id": self.env.ref("product.product_category_1").id,
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            self.pav_3.id,
                            self.pav_4.id,
                        ],
                    )
                ],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_1, 1, self.partner, date=False, uom_id=self.variant_1.uom_id.id
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_2, 1, self.partner, date=False, uom_id=self.variant_2.uom_id.id
        )
        self.assertEqual(res1[0], 35.0)
        self.assertEqual(res2[0], 35.0)

    def test_leg_aluminum_color_white_and_black(self):
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 35.0,
                "applied_on": "2_product_category",
                "categ_id": self.env.ref("product.product_category_1").id,
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            self.pav_2.id,
                            self.pav_3.id,
                            self.pav_4.id,
                        ],
                    )
                ],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_1, 1, self.partner, date=False, uom_id=self.variant_1.uom_id.id
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_2, 1, self.partner, date=False, uom_id=self.variant_2.uom_id.id
        )
        self.assertEqual(res1[0], 35.0)
        self.assertEqual(res2[0], 35.0)
