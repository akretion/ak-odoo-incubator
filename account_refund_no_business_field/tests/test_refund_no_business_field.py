# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestSale(common.TransactionCase):
    def test_refund_no_business_field(self):
        # more kind of functional test because this module aims to fix this specific
        # case.
        sale = self.env.ref("sale.sale_order_7")
        self.assertEqual(sale.invoice_status, "to invoice")
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                active_model="sale.order", active_id=sale.id, active_ids=sale.ids
            )
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        wizard.create_invoices()
        self.assertEqual(sale.invoice_status, "no")
        invoice = sale.invoice_ids
        invoice.action_post()
        refund_wizard = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "journal_id": invoice.journal_id.id,
                    "reason": "no reason",
                    "refund_method": "refund",
                }
            )
        )
        refund_wizard.reverse_moves()
        # Check sale invoice state stay the same which is the main goal of the
        # module
        self.assertEqual(sale.invoice_status, "no")
