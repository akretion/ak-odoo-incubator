# -*- coding: utf-8 -*-
from odoo.addons.queue_job.tests.common import JobMixin
from .common import (
    CommonInvoicing,
    XML_AGREEMENT_1,
    XML_AGREEMENT_2,
    XML_COMPANY_A,
    XML_COMPANY_B,
    XML_COMPANY_HOLDING,
    XML_PARTNER_ID,
)


class TestInvoicing(CommonInvoicing, JobMixin):

    def _start_scenario(
            self, agreement_xml_id, sale_xml_ids, expected_xml_ids):
        "This function will test a full scenario of invoicing."
        # Check if current state of sale order is correct
        sales = self._get_sales(sale_xml_ids)
        self._check_sale_state(sales, 'not_ready')

        # Validate the sale order (sale_xml_ids) and check the state
        self._validate_and_deliver_sale(sale_xml_ids)
        sales = self._get_sales(sale_xml_ids)
        sales_invoiceable = sales.filtered(
            lambda r: r.company_id != r.agreement_id.holding_company_id)
        self._check_sale_state(sales_invoiceable, 'invoiceable')

        # Generate the holding invoice and check the :
        # - sales invoiced
        # - sales state
        # - invoiced amount
        invoice = self._generate_holding_invoice(agreement_xml_id)
        self._check_number_of_invoice(invoice, 1)
        sales_expected = self._get_sales(expected_xml_ids)
        self._check_invoiced_sale_order(invoice, sales_expected)
        self._check_sale_state(sales_expected, 'pending')
        expected_amount = sum(sales_expected.mapped('amount_total'))
        self._check_expected_invoice_amount(invoice, expected_amount)

        # Validate Invoice and check sale invoice state
        invoice.action_invoice_open()
        self._check_sale_state(sales_expected, 'invoiced')

        # Generate the child invoice and check
        # - that child invoice have been generated
        # - that the partner on child invoice is correct
        # - check the invoiced amount
        # - check the sale state
        jobs = self.job_counter()
        sale_companies = sales_invoiceable.mapped('company_id')
        invoice.generate_child_invoice()
        # check that a job have been created for each child company
        self.assertEqual(jobs.count_created(), len(sale_companies))
        self.perform_jobs(jobs)
        self._check_child_invoice(invoice)
        self._check_child_invoice_partner(invoice)
        self._check_child_invoice_amount(invoice)
        return invoice

    def test_invoice_market_1_one_company_one_partner(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_agreement([1, 2], XML_AGREEMENT_1)
        self._set_agreement([3, 4], XML_AGREEMENT_2)
        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
        self._start_scenario(XML_AGREEMENT_1, [1, 2, 3, 4], [1, 2])
        sales = self._get_sales([3, 4])
        self._check_sale_state(sales, 'invoiceable')

    def test_invoice_market_1_multi_company_one_partner(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_agreement([1, 2, 3, 4], XML_AGREEMENT_1)
        self._set_company([1, 2], XML_COMPANY_A)
        self._set_company([3, 4], XML_COMPANY_B)
        self._start_scenario(XML_AGREEMENT_1, [1, 2, 3, 4], [1, 2, 3, 4])

    def test_invoice_market_1_multi_company_with_holding_one_partner(self):
        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
        self._set_agreement([1, 2, 3, 4], XML_AGREEMENT_1)
        self._set_company([1, 2], XML_COMPANY_A)
        self._set_company([3], XML_COMPANY_B)
        self._set_company([4], XML_COMPANY_HOLDING)
        self._start_scenario(XML_AGREEMENT_1, [1, 2, 3, 4], [1, 2, 3])
        sales = self._get_sales([4])
        self._check_sale_state(sales, 'none')
