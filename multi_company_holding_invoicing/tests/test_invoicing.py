# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.tests.common import mock_job_delay_to_direct

from .common import (
    CHILD_JOB_PATH,
    XML_COMPANY_A,
    XML_COMPANY_B,
    XML_COMPANY_HOLDING,
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


class TestInvoicingFromSaleTeam(CommonGenerateInvoice):
    def _start_scenario(self, section_xml_id, sale_xml_ids, expected_xml_ids):
        "This function will test a full scenario of invoicing."
        # Generate the holding invoice and check the :
        # - sales invoiced
        # - sales state
        invoice = self._generate_holding_invoice_from_section(section_xml_id)
        self._check_number_of_invoice(invoice, 1)
        sales_expected = self._get_sales(expected_xml_ids)
        self._check_invoiced_sale_order(invoice, sales_expected)
        self._check_sale_state(sales_expected, "pending")

        # Validad Invoice and check sale invoice state
        invoice.signal_workflow("invoice_open")
        self._check_sale_state(sales_expected, "invoiced")

        # Generate the child invoice and check
        # - that child invoice have been generated
        # - that the partner on child invoice is correct
        # - check the sale state
        with mock_job_delay_to_direct(CHILD_JOB_PATH):
            invoice.generate_child_invoice()
        self._check_child_invoice(invoice)
        self._check_child_invoice_partner(invoice)
        self.invoice = invoice
        self.child_invoice_a = invoice.child_invoice_ids.filtered(
            lambda s: s.company_id == self.company_a
        )
        self.child_invoice_b = invoice.child_invoice_ids.filtered(
            lambda s: s.company_id == self.company_b
        )

    def test_invoice_market_1_one_company_one_partner(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_section([1, 2], XML_SECTION_1)
        self._set_section([3, 4], XML_SECTION_2)
        self._set_company([1, 2, 3, 4], XML_COMPANY_A)

        self._start_scenario(XML_SECTION_1, [1, 2, 3, 4], [1, 2])

        self.assertEqual(self.invoice.amount_untaxed, 3000)
        self.assertEqual(self.child_invoice_a.amount_untaxed, 3000 * 0.9)

        # In this case sale order 3 and 4 should have been not invoiced
        # as they do not belong to section 1
        sales = self._get_sales([3, 4])
        self._check_sale_state(sales, "invoiceable")

    def test_invoice_market_1_multi_company_one_partner(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2], XML_COMPANY_A)
        self._set_company([3, 4], XML_COMPANY_B)
        self._start_scenario(XML_SECTION_1, [1, 2, 3, 4], [1, 2, 3, 4])
        self.assertEqual(self.invoice.amount_untaxed, 3600)
        self.assertEqual(self.child_invoice_a.amount_untaxed, 3000 * 0.9)
        self.assertEqual(self.child_invoice_b.amount_untaxed, 600 * 0.9)

    def test_invoice_market_1_multi_company_with_holding_one_partner(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2], XML_COMPANY_A)
        self._set_company([3], XML_COMPANY_B)
        self._set_company([4], XML_COMPANY_HOLDING)

        self._start_scenario(XML_SECTION_1, [1, 2, 3, 4], [1, 2, 3, 4])

        self.assertEqual(self.invoice.amount_untaxed, 3600)
        self.assertEqual(self.child_invoice_a.amount_untaxed, 3000 * 0.9)
        self.assertEqual(self.child_invoice_b.amount_untaxed, 500 * 0.9)
        sales = self._get_sales([4])
        self._check_sale_state(sales, "invoiced")

    def test_no_fiscal_position(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2], XML_COMPANY_A)
        self._set_company([3], XML_COMPANY_B)
        self._set_company([4], XML_COMPANY_HOLDING)

        self._start_scenario(XML_SECTION_1, [1, 2, 3, 4], [1, 2, 3, 4])

        self.assertEqual(self.invoice.amount_tax, 3600 * 0.05)
        self.assertEqual(self.child_invoice_a.amount_tax, 3000 * 0.9 * 0.05)
        self.assertEqual(self.child_invoice_b.amount_tax, 500 * 0.9 * 0.05)

    def _get_fp_test_id(self, company):
        return (
            self.env["account.fiscal.position"]
            .search(
                [
                    ("company_id", "=", company.id),
                    ("name", "=", "holding-test"),
                ]
            )
            .id
        )

    def test_with_fiscal_position(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_section([1, 2, 3, 4], XML_SECTION_1)
        self._set_company([1, 2], XML_COMPANY_A)
        self._set_company([3], XML_COMPANY_B)
        self._set_company([4], XML_COMPANY_HOLDING)

        partner = self.env.ref(XML_PARTNER_ID)
        for partner in [self.company_a.partner_id, self.company_b.partner_id, partner]:
            partner.with_context(force_company=self.company_holding.id).write(
                {
                    "property_account_position": self._get_fp_test_id(
                        self.company_holding
                    ),
                }
            )
        for company in [self.company_a, self.company_b]:
            self.company_holding.partner_id.with_context(
                force_company=company.id
            ).write({"property_account_position": self._get_fp_test_id(company)})
        self._start_scenario(XML_SECTION_1, [1, 2, 3, 4], [1, 2, 3, 4])
        self.assertEqual(self.invoice.amount_tax, 3600 * 0.10)
        self.assertEqual(self.child_invoice_a.amount_tax, 3000 * 0.9 * 0.10)
        self.assertEqual(self.child_invoice_b.amount_tax, 500 * 0.9 * 0.10)


class TestInvoicingFromSaleTeamGroupBySale(TestInvoicingFromSaleTeam):
    @classmethod
    def setUpClass(cls):
        super(TestInvoicingFromSaleTeamGroupBySale, cls).setUpClass()
        section = cls.env.ref(XML_SECTION_1)
        section.write({"holding_invoice_group_by": "sale"})

    def test_one_invoice_line_per_sale(self):
        self.test_invoice_market_1_multi_company_with_holding_one_partner()
        self.assertEqual(
            [u"SO008 - Custom REF 1", u"SO009", u"SO010 - Custom REF 3", u"SO011"],
            self.invoice.invoice_line.mapped("name"),
        )
        self.assertEqual(
            [u"SO008 - Custom REF 1", u"SO009", u"SO010 - Custom REF 3", u"SO011"],
            self.invoice.invoice_line.mapped("name"),
        )
        self.assertEqual(
            [u"SO008 - Custom REF 1", u"SO009", u"Holding Royalty Product"],
            self.child_invoice_a.invoice_line.mapped("name"),
        )
        self.assertEqual(
            [u"SO010 - Custom REF 3", u"Holding Royalty Product"],
            self.child_invoice_b.invoice_line.mapped("name"),
        )
