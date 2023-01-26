# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.product_supplierinfo_intercompany.tests.test_supplier_intercompany import (
    TestIntercompanySupplierCase,
)


class TestIntercompanySupplier(TestIntercompanySupplierCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("product.product_product_2_product_template")
        cls.attr_leg = cls.env.ref("product.product_attribute_1")
        cls.pav_steel = cls.env.ref("product.product_attribute_value_1")
        cls.pav_alu = cls.env.ref("product.product_attribute_value_2")
        cls.attr_color = cls.env.ref("product.product_attribute_2")
        cls.pav_white = cls.env.ref("product.product_attribute_value_3")
        cls.pav_black = cls.env.ref("product.product_attribute_value_4")
        cls.pricelist = cls.env.ref(
            "product_supplierinfo_intercompany.pricelist_intercompany"
        )
        cls.item = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "product_tmpl_id": cls.template.id,
                "base": "list_price",
                "price_discount": 0,
                "fixed_price": 20,
                "product_attribute_value_ids": [(6, 0, [cls.pav_alu.id])],
            }
        )

    def test_create_item_with_attribute(self):
        supplierinfo = self._get_supplier_info(self.template)
        self.assertEqual(len(supplierinfo), 1)
        self.assertEqual(len(supplierinfo.intercompany_pricelist_id), 1)
        self.assertEqual(supplierinfo.product_attribute_value_ids, self.pav_alu)

    def test_item_add_attribute(self):
        self.item.product_attribute_value_ids |= self.pav_black
        supplierinfo = self._get_supplier_info(self.template)
        self.assertEqual(len(supplierinfo), 1)
        self.assertEqual(len(supplierinfo.intercompany_pricelist_id), 1)
        self.assertEqual(
            supplierinfo.product_attribute_value_ids, self.pav_alu + self.pav_black
        )

    def test_item_remove_attribute(self):
        self.item.product_attribute_value_ids = None
        supplierinfo = self._get_supplier_info(self.template)
        self.assertEqual(len(supplierinfo), 1)
        self.assertEqual(len(supplierinfo.intercompany_pricelist_id), 1)
        self.assertFalse(supplierinfo.product_attribute_value_ids)

    def test_item_change_attribute(self):
        self.item.product_attribute_value_ids = self.pav_black
        supplierinfo = self._get_supplier_info(self.template)
        self.assertEqual(len(supplierinfo), 1)
        self.assertEqual(len(supplierinfo.intercompany_pricelist_id), 1)
        self.assertEqual(supplierinfo.product_attribute_value_ids, self.pav_black)
