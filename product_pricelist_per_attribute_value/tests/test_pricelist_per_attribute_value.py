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
        cls.list1 = cls.env["product.pricelist"].create({"name": "Pricelist 1"})
        cls.pricelist_item_global = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.list1.id,
                "compute_price": "fixed",
                "fixed_price": 45.0,
                "applied_on": "3_global",
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.pav_2.id,
                            cls.pav_3.id,
                        ],
                    )
                ],
            }
        )
        cls.list2 = cls.env["product.pricelist"].create({"name": "Pricelist 2"})
        cls.pricelist_item_category = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.list2.id,
                "compute_price": "fixed",
                "fixed_price": 35.0,
                "applied_on": "2_product_category",
                "categ_id": cls.env.ref("product.product_category_1").id,
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.pav_2.id,
                            cls.pav_3.id,
                        ],
                    )
                ],
            }
        )
        cls.list3 = cls.env["product.pricelist"].create({"name": "Pricelist 3"})
        cls.pricelist_item_product = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.list3.id,
                "compute_price": "fixed",
                "fixed_price": 25.0,
                "applied_on": "1_product",
                "product_tmpl_id": cls.env.ref(
                    "product.product_product_4_product_template"
                ).id,
                "product_attribute_value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.pav_2.id,
                            cls.pav_3.id,
                        ],
                    )
                ],
            }
        )
        # ==== Sale Orders ====
        cls.order1 = cls.env.ref("sale.sale_order_1")
        cls.sale_order_line_1 = cls.env.ref("sale.sale_order_line_1")
        # ==== Products ====
        cls.product_product_4 = cls.env.ref("product.product_product_4")
        # ==== Product Template Attribute Lines ====
        cls.ptal_attribute1_value2 = cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.product_product_4.product_tmpl_id.id,
                "attribute_id": cls.env.ref("product.product_attribute_1").id,
                "value_ids": [(6, 0, [cls.pav_2.id])],
            }
        )
        cls.ptal_attribute2_value3 = cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.product_product_4.product_tmpl_id.id,
                "attribute_id": cls.env.ref("product.product_attribute_2").id,
                "value_ids": [(6, 0, [cls.pav_3.id])],
            }
        )
        cls.ptal_attribute2_value4 = cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.product_product_4.product_tmpl_id.id,
                "attribute_id": cls.env.ref("product.product_attribute_2").id,
                "value_ids": [(6, 0, [cls.pav_4.id])],
            }
        )
        # ==== Product Template Attribute Values ====
        cls.ptav_attribute1_value2 = (
            cls.ptal_attribute1_value2.product_template_value_ids.filtered(
                lambda ptv: ptv.product_attribute_value_id.id == 2
            )
        )
        cls.ptav_attribute2_value3 = (
            cls.ptal_attribute2_value3.product_template_value_ids.filtered(
                lambda ptv: ptv.product_attribute_value_id.id == 3
            )
        )
        cls.ptav_attribute2_value4 = (
            cls.ptal_attribute2_value4.product_template_value_ids.filtered(
                lambda ptv: ptv.product_attribute_value_id.id == 4
            )
        )
        cls.ptav_attribute1_value2_attribute2_value4 = (
            cls.ptav_attribute1_value2 | cls.ptav_attribute2_value4
        )

    def test_pricelist_item_name(self):
        self.assertEqual(
            self.pricelist_item_global.name, "All Products (Aluminium, White)"
        )
        self.assertEqual(
            self.pricelist_item_category.name,
            "Category: All / Saleable (Aluminium, White)",
        )
        self.assertEqual(
            self.pricelist_item_product.name,
            "Product: Customizable Desk (CONFIG) (Aluminium, White)",
        )

    def test_pricelist_item_with_one_attribute_value(self):
        # update pricelist with only one attribute value
        self.pricelist_item_product.product_attribute_value_ids = self.pav_3
        self.pricelist_item_global.product_attribute_value_ids = self.pav_3
        self.pricelist_item_category.product_attribute_value_ids = self.pav_3
        # update product_4 with only one product template attribute value
        self.product_product_4.product_template_attribute_value_ids = (
            self.ptav_attribute2_value3
        )
        # update sale_order_line_1 with product_4
        self.sale_order_line_1.write({"product_id": self.product_product_4.id})
        # update sale_order1 with pricelist 1
        self.order1.write({"pricelist_id": self.list1.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 1
        self.assertEqual(self.sale_order_line_1.price_unit, 45.0)
        # update sale order1 with pricelist 2
        self.order1.write({"pricelist_id": self.list2.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 2
        self.assertEqual(self.sale_order_line_1.price_unit, 35.0)
        # update sale order1 with pricelist 3
        self.order1.write({"pricelist_id": self.list3.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 3
        self.assertEqual(self.sale_order_line_1.price_unit, 25.0)

    def test_pricelist_item_with_two_attribute_values_of_same_attribute(self):
        # update pricelist with two attribute value
        self.pricelist_item_product.product_attribute_value_ids = [
            (6, 0, [self.pav_3.id, self.pav_4.id])
        ]
        self.pricelist_item_global.product_attribute_value_ids = [
            (6, 0, [self.pav_3.id, self.pav_4.id])
        ]
        self.pricelist_item_category.product_attribute_value_ids = [
            (6, 0, [self.pav_3.id, self.pav_4.id])
        ]
        # update product_4 with only one product template attribute value
        self.product_product_4.product_template_attribute_value_ids = (
            self.ptav_attribute2_value4
        )
        # update sale_order_line_1 with product_4
        self.sale_order_line_1.write({"product_id": self.product_product_4.id})
        # update sale_order1 with pricelist 1
        self.order1.write({"pricelist_id": self.list1.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 1
        self.assertEqual(self.sale_order_line_1.price_unit, 45.0)
        # update sale order1 with pricelist 2
        self.order1.write({"pricelist_id": self.list2.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 2
        self.assertEqual(self.sale_order_line_1.price_unit, 35.0)
        # update sale order1 with pricelist 3
        self.order1.write({"pricelist_id": self.list3.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 3
        self.assertEqual(self.sale_order_line_1.price_unit, 25.0)

    def test_pricelist_item_with_three_attribute_values_of_different_attributes(self):
        # update pricelist with three attribute value
        self.pricelist_item_product.product_attribute_value_ids = [
            (6, 0, [self.pav_2.id, self.pav_3.id, self.pav_4.id])
        ]
        self.pricelist_item_global.product_attribute_value_ids = [
            (6, 0, [self.pav_2.id, self.pav_3.id, self.pav_4.id])
        ]
        self.pricelist_item_category.product_attribute_value_ids = [
            (6, 0, [self.pav_2.id, self.pav_3.id, self.pav_4.id])
        ]
        # update product_4 with two product template attribute values
        self.product_product_4.product_template_attribute_value_ids = (
            self.ptav_attribute1_value2_attribute2_value4
        )
        # update sale_order_line_1 with product_4
        self.sale_order_line_1.write({"product_id": self.product_product_4.id})
        # update sale_order1 with pricelist 1
        self.order1.write({"pricelist_id": self.list1.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 1
        self.assertEqual(self.sale_order_line_1.price_unit, 45.0)
        # update sale order1 with pricelist 2
        self.order1.write({"pricelist_id": self.list2.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 2
        self.assertEqual(self.sale_order_line_1.price_unit, 35.0)
        # update sale order1 with pricelist 3
        self.order1.write({"pricelist_id": self.list3.id})
        self.order1.update_prices()
        # check that the unit price of sale_order_line_1 is the one in the pricelist 3
        self.assertEqual(self.sale_order_line_1.price_unit, 25.0)
