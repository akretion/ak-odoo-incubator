# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestSaleCertificatTypology(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product_7 = cls.env.ref("product.product_product_7")
        cls.product_6 = cls.env.ref("product.product_product_6")
        cls.professional_card = cls.env["certificat.typology"].create(
            {"name": "Professional card"}
        )
        cls.product_6.write(
            {"required_certificat_ids": [(6, 0, cls.professional_card.ids)]}
        )
        cls.id_card = cls.env["certificat.typology"].create({"name": "ID card"})
        cls.product_7.write({"required_certificat_ids": [(6, 0, cls.id_card.ids)]})
        cls.partner = cls.env.ref("base.res_partner_1")

    def test_create_certificat_item(self):
        sale_order = self._create_sale_order(self.partner, self.product_6)
        self.assertEqual(len(sale_order.certificat_item_ids), 1)
        self.assertEqual(
            sale_order.certificat_item_ids[0].certificat_typology_id,
            self.professional_card,
        )

    def test_unlink_certificat_item(self):
        sale_order = self._create_sale_order(self.partner, self.product_6)
        sale_order.order_line.unlink()
        self.assertEqual(len(sale_order.certificat_item_ids), 0)

    def test_change_certificat_item_after_change_product(self):
        sale_order = self._create_sale_order(self.partner, self.product_6)
        sale_order.order_line.write({"product_id": self.product_7.id})
        self.assertEqual(
            sale_order.certificat_item_ids[0].certificat_typology_id, self.id_card
        )

    def _create_sale_order(self, partner, product):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
        return order_form.save()
