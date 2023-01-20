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
        cls.attr_leg = cls.env.ref("product.product_attribute_1")
        cls.pav_steel = cls.env.ref("product.product_attribute_value_1")
        cls.pav_alu = cls.env.ref("product.product_attribute_value_2")
        cls.attr_color = cls.env.ref("product.product_attribute_2")
        cls.pav_white = cls.env.ref("product.product_attribute_value_3")
        cls.pav_black = cls.env.ref("product.product_attribute_value_4")
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
                            "attribute_id": cls.attr_leg.id,
                            "value_ids": [cls.pav_steel.id, cls.pav_alu.id],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attr_color.id,
                            "value_ids": [cls.pav_white.id, cls.pav_black.id],
                        },
                    ),
                ],
            }
        )
        cls.variant_alu_white = cls._get_variant(cls.pav_alu | cls.pav_white)
        cls.variant_alu_black = cls._get_variant(cls.pav_alu | cls.pav_black)
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
                            self.pav_alu.id,
                            self.pav_white.id,
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
                "product_attribute_value_ids": [(6, 0, [self.pav_alu.id])],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_alu_white,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_white.uom_id.id,
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_alu_black,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_black.uom_id.id,
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
                            self.pav_alu.id,
                            self.pav_white.id,
                        ],
                    )
                ],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_alu_white,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_white.uom_id.id,
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_alu_black,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_black.uom_id.id,
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
                            self.pav_white.id,
                            self.pav_black.id,
                        ],
                    )
                ],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_alu_white,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_white.uom_id.id,
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_alu_black,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_black.uom_id.id,
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
                            self.pav_alu.id,
                            self.pav_white.id,
                            self.pav_black.id,
                        ],
                    )
                ],
            }
        )
        res1 = self.pricelist.get_product_price_rule(
            self.variant_alu_white,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_white.uom_id.id,
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_alu_black,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_black.uom_id.id,
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
                "product_attribute_value_ids": [(6, 0, [self.pav_alu.id])],
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
            self.variant_alu_white,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_white.uom_id.id,
        )
        res2 = self.pricelist.get_product_price_rule(
            self.variant_alu_black,
            1,
            self.partner,
            date=False,
            uom_id=self.variant_alu_black.uom_id.id,
        )
        self.assertEqual(res1[0], 45.0)
        self.assertEqual(res2[0], 45.0)
