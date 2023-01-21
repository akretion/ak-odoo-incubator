# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class TestSupplier(SavepointCase):
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
        cls.variant_steel_black = cls._get_variant(cls.pav_steel | cls.pav_black)

        # ==== Partners ====
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.template_seller = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.template.id,
                "name": cls.partner.id,
                "price": 1,
            }
        )
        cls.variant_alu_white_seller = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.template.id,
                "product_id": cls.variant_alu_white.id,
                "name": cls.partner.id,
                "price": 5,
            }
        )
        cls.variant_alu_seller = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.template.id,
                "product_attribute_value_ids": [(6, 0, [cls.pav_alu.id])],
                "name": cls.partner.id,
                "price": 15,
            }
        )

    def test_supplier_on_template(self):
        seller = self.variant_steel_black._select_seller(partner_id=self.partner)
        self.assertEqual(self.template_seller, seller)

    def test_supplier_on_variant(self):
        seller = self.variant_alu_white._select_seller(partner_id=self.partner)
        self.assertEqual(self.variant_alu_white_seller, seller)

    def test_supplier_on_attribute(self):
        seller = self.variant_alu_black._select_seller(partner_id=self.partner)
        self.assertEqual(self.variant_alu_seller, seller)
