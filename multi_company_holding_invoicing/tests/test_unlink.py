# -*- coding: utf-8 -*-
from .common import (
    CommonInvoicing,
    XML_AGREEMENT_1,
    XML_COMPANY_A,
    XML_PARTNER_ID,
)


class TestUnlink(CommonInvoicing):

    def test_invoice_market_1_one_company_one_partner(self):
        self._set_partner([1, 2], XML_PARTNER_ID)
        self._set_agreement([1, 2], XML_AGREEMENT_1)
        self._set_company([1, 2], XML_COMPANY_A)
        self._validate_and_deliver_sale([1, 2])
        invoice = self._generate_holding_invoice(XML_AGREEMENT_1)
        sales = self._get_sales([1, 2])
        self._check_sale_state(sales, 'pending')
        invoice.unlink()
        self._check_sale_state(sales, 'invoiceable')
