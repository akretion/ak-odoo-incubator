from odoo import Command as cmd
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestBlock(TransactionCase):
    def test_blocked(self):
        partner = self.env["res.partner"].create({"name": "Test"})
        product = self.env["product.product"].create({"name": "Test"})
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [cmd.create({"product_id": product.id})],
            }
        )
        po = self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [cmd.create({"product_id": product.id})],
            }
        )
        with self.assertRaises(UserError):
            so.action_confirm()
        with self.assertRaises(UserError):
            po.button_confirm()
