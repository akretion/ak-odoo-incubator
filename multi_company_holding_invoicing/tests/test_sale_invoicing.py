# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from openerp.exceptions import Warning as UserError

from .common import (
    XML_COMPANY_A,
    XML_PARTNER_ID,
    XML_SECTION_1,
    XML_SECTION_2,
    CommonGenerateInvoice,
)

# Reminder
# Sale 1: amount untaxed = 2000
# Sale 2: amount untaxed = 1000
# Sale 3: amount untaxed = 500
# Sale 4: amount untaxed = 100
# Sale 5: amount untaxed = 50
# Royalty 10 %


class TestInvoicingFromSaleOrder(CommonGenerateInvoice):
    def _make_invoice(self, sale_xml_ids):
        sales = self._get_sales(sale_xml_ids)
        return (
            self.env["sale.make.invoice"]
            .with_context(active_ids=sales.ids)
            .create(
                {
                    "invoice_date": datetime.today(),
                }
            )
        )

    def _start_scenario(self, sale_xml_ids, expected_xml_ids):
        # Generate the holding invoice and check the :
        # - sales invoiced
        # - sales state
        # - invoiced amount
        wizard = self._make_invoice(sale_xml_ids)
        res = wizard.make_invoices()
        invoice = self.env["account.invoice"].browse(res["domain"][0][2])

        self._check_number_of_invoice(invoice, 1)
        sales_expected = self._get_sales(expected_xml_ids)
        self._check_invoiced_sale_order(invoice, sales_expected)
        self._check_sale_state(sales_expected, "pending")

        # Validad Invoice and check sale invoice state
        invoice.signal_workflow("invoice_open")
        self._check_sale_state(sales_expected, "invoiced")

        self.invoice = invoice

    def test_invoice_market_1_one_company_one_partner(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
        self.env.ref(XML_SECTION_1).holding_invoice_generated_by = "child"
        self._start_scenario([1, 2], [1, 2])
        self.assertEqual(self.invoice.amount_untaxed, 3000)
        sales = self._get_sales([3, 4])
        self._check_sale_state(sales, "invoiceable")

    def test_have_error_message_holding(self):
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
        self.env.ref(XML_SECTION_1).holding_invoice_generated_by = "holding"
        wizard = self._make_invoice([1, 2, 3, 4])
        self.assertIn("must be invoiced from the holding company", wizard.error)

    def test_have_error_message_section(self):
        self._set_section([1, 2], XML_SECTION_1)
        self._set_section([3, 4], XML_SECTION_2)
        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
        self.env.ref(XML_SECTION_1).holding_invoice_generated_by = "child"
        self.env.ref(XML_SECTION_2).holding_invoice_generated_by = "child"
        wizard = self._make_invoice([1, 2, 3, 4])
        self.assertEqual("Holding Invoice must be invoiced per section", wizard.error)

    def test_no_error_message(self):
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
        self.env.ref(XML_SECTION_1).holding_invoice_generated_by = "child"
        date_invoice = datetime.today()
        wizard = self._make_invoice([1, 2, 3, 4])
        self.assertFalse(wizard.error)

    def test_raise_error(self):
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
        self.env.ref(XML_SECTION_1).holding_invoice_generated_by = "holding"
        with self.assertRaises(UserError) as error:
            wizard = self._make_invoice([1, 2, 3, 4])
            wizard.make_invoices()
        self.assertIn(
            "must be invoiced from the holding company", error.exception.message
        )
