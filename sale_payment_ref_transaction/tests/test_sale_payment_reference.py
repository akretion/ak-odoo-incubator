# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class TestSalePyamentReferenceTransaction(TransactionCase):
    def test_sale_payment_ref(self):
        partner = self.env.ref("base.res_partner_1")
        product = self.env.ref("product.product_product_16")
        product.write({"invoice_policy": "order"})
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        self.env["payment.transaction"].create(
            {
                "reference": "123456789",
                "partner_id": partner.id,
                "acquirer_id": self.env.ref("payment.payment_acquirer_transfer").id,
                "amount": so.amount_total,
                "currency_id": so.currency_id.id,
                "sale_order_ids": [(6, 0, so.ids)],
            }
        )
        so.action_confirm()
        invoice_wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_model="sale.order", active_ids=so.ids)
            .create({})
        )
        invoice_wizard.create_invoices()
        self.assertEqual(so.reference, "123456789")
        self.assertEqual(so.invoice_ids.payment_reference, "123456789")
