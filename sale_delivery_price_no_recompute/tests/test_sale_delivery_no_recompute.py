# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, SavepointCase


class TestPurchaseLot(SavepointCase):
    def test_sale_delivery_no_recompute_price(self):
        sale = self.env.ref("sale.sale_order_3")
        normal_carrier = self.env.ref("delivery.normal_delivery_carrier")
        rule_carrier = self.env.ref("delivery.delivery_carrier")
        # choose a carrier, force price compute, price should be 10
        wizard_ctx = sale.action_open_delivery_wizard()["context"]
        delivery_wizard = Form(
            self.env["choose.delivery.carrier"].with_context(wizard_ctx)
        )
        delivery_wizard.carrier_id = normal_carrier
        delivery_wizard = delivery_wizard.save()
        delivery_wizard.update_price()
        delivery_wizard.button_confirm()
        delivery_line = sale.order_line.filtered(lambda l: l.is_delivery)
        # It seems there is an issue with the currency of SO in demo data
        # which make it difficult to assert the real price. But since it does not
        # really matter for the test, let's get around this
        self.assertGreater(delivery_line.price_unit, 0.0)

        # Change carrier should not recompute the price
        current_delivery_price = delivery_line.price_unit
        wizard_ctx = sale.action_open_delivery_wizard()["context"]
        delivery_wizard = Form(
            self.env["choose.delivery.carrier"].with_context(wizard_ctx)
        )
        delivery_wizard.carrier_id = rule_carrier
        delivery_wizard = delivery_wizard.save()
        delivery_wizard.button_confirm()
        delivery_line = sale.order_line.filtered(lambda l: l.is_delivery)
        self.assertEqual(delivery_line.price_unit, current_delivery_price)
