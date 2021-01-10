# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from .common import XML_COMPANY_A, XML_PARTNER_ID, XML_SECTION_1, CommonGenerateInvoice


class TestUnlink(CommonGenerateInvoice):
    def test_invoice_market_1_one_company_one_partner(self):
        self._set_partner([1, 2], XML_PARTNER_ID)
        self._set_section([1, 2], XML_SECTION_1)
        self._set_company([1, 2], XML_COMPANY_A)
        invoice = self._generate_holding_invoice_from_section(XML_SECTION_1)
        sales = self._get_sales([1, 2])
        self._check_sale_state(sales, "pending")
        invoice.unlink()
        self._check_sale_state(sales, "invoiceable")
