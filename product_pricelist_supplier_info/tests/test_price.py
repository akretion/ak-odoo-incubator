# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class TestPrice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Supplier"})
        size, color = cls.env["product.attribute"].create(
            [{"name": "T Size"}, {"name": "T Color"}]
        )
        c_blue, c_green, c_red, s_m, s_l, s_xl = cls.env[
            "product.attribute.value"
        ].create(
            [
                {"attribute_id": color.id, "name": "Blue"},
                {"attribute_id": color.id, "name": "Green"},
                {"attribute_id": color.id, "name": "Red"},
                {"attribute_id": size.id, "name": "M"},
                {"attribute_id": size.id, "name": "L"},
                {"attribute_id": size.id, "name": "XL"},
            ]
        )
        cls.c_green = c_green
        cls.c_red = c_red

        cls.t_shirt = cls.env["product.template"].create(
            {
                "name": "T-shirt",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": size.id,
                            "value_ids": [s_m.id, s_l.id, s_xl.id],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": color.id,
                            "value_ids": [c_blue.id, c_green.id, c_red.id],
                        },
                    ),
                ],
            }
        )

        def get_product(values):
            for variant in cls.t_shirt.product_variant_ids:
                tmpl_values = variant.product_template_attribute_value_ids
                if tmpl_values.product_attribute_value_id == values:
                    return variant

        cls.t_shirt_green_xl = get_product(s_xl | c_green)
        cls.t_shirt_green_l = get_product(s_l | c_green)
        cls.t_shirt_red_l = get_product(s_l | c_red)
        cls.t_shirt.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.partner.id,
                            "product_tmpl_id": cls.t_shirt.id,
                            "product_id": cls.t_shirt_green_xl.id,
                            "price": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.partner.id,
                            "product_tmpl_id": cls.t_shirt.id,
                            "product_id": cls.t_shirt_green_xl.id,
                            "price": 50,
                            "min_qty": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.partner.id,
                            "product_tmpl_id": cls.t_shirt.id,
                            "product_attribute_value_ids": [(6, 0, [c_green.id])],
                            "price": 90,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.partner.id,
                            "product_tmpl_id": cls.t_shirt.id,
                            "product_attribute_value_ids": [(6, 0, [c_green.id])],
                            "price": 45,
                            "min_qty": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.partner.id,
                            "product_tmpl_id": cls.t_shirt.id,
                            "price": 80,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.partner.id,
                            "product_tmpl_id": cls.t_shirt.id,
                            "price": 40,
                            "min_qty": 100,
                        },
                    ),
                ]
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Price per product"}
        )

    def _create_price_item(self, list_vals):
        for vals in list_vals:
            if vals.get("product"):
                vals["product_id"] = vals.pop("product").id
            if vals.get("attr_values"):
                vals["product_attribute_value_ids"] = [
                    (6, 0, vals.pop("attr_values").ids)
                ]
            vals["fixed_price"] = vals.pop("price")
            vals.update(
                {
                    "pricelist_id": self.pricelist.id,
                    "product_tmpl_id": self.t_shirt.id,
                }
            )
        return self.env["product.pricelist.item"].create(list_vals)

    def _assert_item(self, item, price, info=""):
        self.assertEqual(item.main_supplier_partner_id, self.partner)
        self.assertEqual(item.main_supplier_price, price)
        self.assertEqual(item.main_supplier_info, info)

    def test_pricelist_product(self):
        (
            green_xl,
            green_xl_50,
            green_xl_100,
            green_xl_200,
            green_l,
            green_l_100,
            red_l,
            red_l_100,
        ) = self._create_price_item(
            [
                {"product": self.t_shirt_green_xl, "price": 200},
                {"product": self.t_shirt_green_xl, "price": 180, "min_quantity": 50},
                {"product": self.t_shirt_green_xl, "price": 160, "min_quantity": 100},
                {"product": self.t_shirt_green_xl, "price": 140, "min_quantity": 200},
                {"product": self.t_shirt_green_l, "price": 180},
                {"product": self.t_shirt_green_l, "price": 140, "min_quantity": 100},
                {"product": self.t_shirt_red_l, "price": 160},
                {"product": self.t_shirt_red_l, "price": 120, "min_quantity": 100},
            ]
        )
        # check margin once
        self.assertEqual(green_xl.main_supplier_margin, 100)

        self._assert_item(green_xl, 100)
        self._assert_item(green_xl_50, 100)
        self._assert_item(green_xl_100, 50)
        self._assert_item(green_xl_200, 50)
        self._assert_item(green_l, 90)
        self._assert_item(green_l_100, 45)
        self._assert_item(red_l, 80)
        self._assert_item(red_l_100, 40)

    def test_pricelist_attribute(self):
        # vert => info + mx price
        # rouge > template
        # rouge + vert => info + max price
        c_green = self.c_green
        c_red = self.c_red
        (
            green,
            green_50,
            green_100,
            green_200,
            red,
            red_100,
            red_green,
            red_green_100,
        ) = self._create_price_item(
            [
                {"attr_values": c_green, "price": 200},
                {"attr_values": c_green, "price": 180, "min_quantity": 50},
                {"attr_values": c_green, "price": 160, "min_quantity": 100},
                {"attr_values": c_green, "price": 140, "min_quantity": 200},
                {"attr_values": c_red, "price": 180},
                {"attr_values": c_red, "price": 140, "min_quantity": 100},
                {"attr_values": c_red | c_green, "price": 160},
                {"attr_values": c_red | c_green, "price": 120, "min_quantity": 100},
            ]
        )
        self._assert_item(green, 100, "- XL, Green: 100\n- Green: 90")
        self._assert_item(green_50, 100, "- XL, Green: 100\n- Green: 90")
        self._assert_item(green_100, 50, "- XL, Green: 50\n- Green: 45")
        self._assert_item(green_200, 50, "- XL, Green: 50\n- Green: 45")
        self._assert_item(red, 80)
        self._assert_item(red_100, 40)
        self._assert_item(
            red_green, 100, "- XL, Green: 100\n- Green: 90\n- _: 80")
        self._assert_item(
            red_green_100, 50, "- XL, Green: 50\n- Green: 45\n- _: 40")

    def test_pricelist_template(self):
        qty_1, qty_50, qty_100, qty_200 = self._create_price_item([
            {"price": 200},
            {"price": 180, "min_quantity": 50},
            {"price": 160, "min_quantity": 100},
            {"price": 140, "min_quantity": 200},
            ])
        self._assert_item(qty_1, 100, "- XL, Green: 100\n- Green: 90\n- _: 80")
        self._assert_item(qty_50, 100, "- XL, Green: 100\n- Green: 90\n- _: 80")
        self._assert_item(qty_100, 50, "- XL, Green: 50\n- Green: 45\n- _: 40")
        self._assert_item(qty_200, 50, "- XL, Green: 50\n- Green: 45\n- _: 40")
