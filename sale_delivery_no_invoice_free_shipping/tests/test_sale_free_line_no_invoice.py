# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestSaleNoInvoicingFreeLine(TransactionCase):
    def test_sale_free_line_no_invoice(self):
        sale = self.env.ref("sale.sale_order_3")
        # add free shipping free
        free_carrier = self.env.ref("delivery.free_delivery_carrier")
        wizard_ctx = sale.action_open_delivery_wizard()["context"]
        delivery_wizard = Form(
            self.env["choose.delivery.carrier"].with_context(**wizard_ctx)
        )
        delivery_wizard.carrier_id = free_carrier
        delivery_wizard = delivery_wizard.save()
        delivery_wizard.button_confirm()

        sale.order_line.product_id.write({"invoice_policy": "order"})
        sale.action_confirm()
        delivery_line = sale.order_line.filtered(lambda li: li.is_delivery)
        self.assertEqual(delivery_line.invoice_status, "invoiced")

        # invoice sale order and check the shipping fee is not in
        context = {
            "active_model": "sale.order",
            "active_ids": [sale.id],
            "active_id": sale.id,
        }
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(**context)
            .create({"advance_payment_method": "delivered"})
        )
        payment.create_invoices()
        invoice = sale.invoice_ids[0]
        shipping_invoice_line = invoice.invoice_line_ids.filtered(
            lambda li: li.product_id == delivery_line.product_id
        )
        self.assertFalse(shipping_invoice_line)
