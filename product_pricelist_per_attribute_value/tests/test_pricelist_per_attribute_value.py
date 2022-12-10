# Copyright 2021 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestPriceListPerAttributeValue(SavepointCase):
    @classmethod
    def _get_variant(cls, values):
        return cls.template.product_variant_ids.filtered(
            lambda s: s.product_template_attribute_value_ids.product_attribute_value_id
            == values
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ==== Product Attribute Values ====
        cls.attr_1 = cls.env.ref("product.product_attribute_1")  # Leg
        cls.pav_1 = cls.env.ref("product.product_attribute_value_1")  # Steel
        cls.pav_2 = cls.env.ref("product.product_attribute_value_2")  # Aluminium
        cls.attr_2 = cls.env.ref("product.product_attribute_2")  # Color
        cls.pav_3 = cls.env.ref("product.product_attribute_value_3")  # White
        cls.pav_4 = cls.env.ref("product.product_attribute_value_4")  # Black
        # ==== Pricelist ====
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Pricelist 1"})
        # ==== Products ====
        cls.template = cls.env["product.template"].create(
            {
                "name": "Table",
                "list_price": 100,
                "categ_id": cls.env.ref("product.product_category_1").id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attr_1.id,
                            "value_ids": [cls.pav_1.id, cls.pav_2.id],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attr_2.id,
                            "value_ids": [cls.pav_3.id, cls.pav_4.id],
                        },
                    ),
                ],
            }
        )
        # Aluminium White
        cls.variant_1 = cls._get_variant(cls.pav_2 | cls.pav_3)
        # Aluminium Black
        cls.variant_2 = cls._get_variant(cls.pav_2 | cls.pav_4)
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
            "Product: Table (Aluminium, White)",
        )

    def test_leg_aluminum(self):
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 45.0,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [(6, 0, [self.pav_2.id])],
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
        self.assertEqual(res2[0], 100)

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

    def test_global_and_leg_aluminum(self):
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 45.0,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [(6, 0, [self.pav_2.id])],
            }
        )
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "compute_price": "fixed",
                "fixed_price": 40.0,
                "applied_on": "1_product",
                "product_tmpl_id": self.template.id,
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
