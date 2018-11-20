# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

#from .common import (
#    CommonInvoicing,
#    XML_AGREEMENT_1,
#    XML_AGREEMENT_2,
#    XML_COMPANY_A,
#    XML_PARTNER_ID,
#    )
#from odoo.exceptions import UserError
#from datetime import datetime
#
#
#class TestChildInvoicing(CommonInvoicing):
#
#    def _start_scenario(self, sale_xml_ids, expected_xml_ids):
#        # Check if current state of sale order is correct
#        sales = self._get_sales(sale_xml_ids)
#        self._check_sale_state(sales, 'not_ready')
#
#        # Validate the sale order (sale_xml_ids) and check the state
#        self._validate_and_deliver_sale(sale_xml_ids)
#        sales = self._get_sales(expected_xml_ids)
#        self._check_sale_state(sales, 'invoiceable')
#
#        # Generate the holding invoice and check the :
#        # - sales invoiced
#        # - sales state
#        # - invoiced amount
#        invoice = self._generate_holding_invoice_from_sale(sales)
#        self._check_number_of_invoice(invoice, 1)
#        sales_expected = self._get_sales(expected_xml_ids)
#        self._check_invoiced_sale_order(invoice, sales_expected)
#        self._check_sale_state(sales_expected, 'pending')
#        expected_amount = sum(sales_expected.mapped('amount_total'))
#        self._check_expected_invoice_amount(invoice, expected_amount)
#
#        # Validad Invoice and check sale invoice state
#        invoice.signal_workflow('invoice_open')
#        self._check_sale_state(sales_expected, 'invoiced')
#
#    def test_invoice_market_1_one_company_one_partner(self):
#        self._set_partner([1, 2, 3, 4], XML_PARTNER_ID)
#        self._set_agreement([1, 2, 3, 4], XML_AGREEMENT_1)
#        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
#        self.env.ref(XML_AGREEMENT_1).holding_invoice_generated_by = 'child'
#        self._start_scenario([1, 2, 3, 4], [1, 2])
#        sales = self._get_sales([3, 4])
#        self._check_sale_state(sales, 'invoiceable')
#
#    def test_have_error_message_holding(self):
#        self._set_agreement([1, 2, 3, 4], XML_AGREEMENT_1)
#        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
#        self.env.ref(XML_AGREEMENT_1).holding_invoice_generated_by = 'holding'
#        invoice_date = datetime.today()
#        self._validate_and_deliver_sale([1, 2, 3, 4])
#        sales = self._get_sales([1, 2, 3, 4])
#        wizard = self.env['sale.make.invoice']\
#            .with_context(active_ids=sales.ids).create({
#                'invoice_date': invoice_date,
#            })
#        self.assertIn('must be invoiced from the holding company',
#                      wizard.error)
#
#    def test_have_error_message_agreement(self):
#        self._set_agreement([1, 2], XML_AGREEMENT_1)
#        self._set_agreement([3, 4], XML_AGREEMENT_2)
#        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
#        self.env.ref(XML_AGREEMENT_1).holding_invoice_generated_by = 'child'
#        self.env.ref(XML_AGREEMENT_2).holding_invoice_generated_by = 'child'
#        invoice_date = datetime.today()
#        self._validate_and_deliver_sale([1, 2, 3, 4])
#        sales = self._get_sales([1, 2, 3, 4])
#        wizard = self.env['sale.make.invoice']\
#            .with_context(active_ids=sales.ids).create({
#                'invoice_date': invoice_date,
#            })
#        self.assertEqual(
#            'Holding Invoice must be invoiced per agreement', wizard.error)
#
#    def test_no_error_message(self):
#        self._set_agreement([1, 2, 3, 4], XML_AGREEMENT_1)
#        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
#        self.env.ref(XML_AGREEMENT_1).holding_invoice_generated_by = 'child'
#        invoice_date = datetime.today()
#        self._validate_and_deliver_sale([1, 2, 3, 4])
#        sales = self._get_sales([1, 2, 3, 4])
#        wizard = self.env['sale.make.invoice']\
#            .with_context(active_ids=sales.ids).create({
#                'invoice_date': invoice_date,
#            })
#        self.assertFalse(wizard.error)
#
#    def test_raise_error(self):
#        self._set_agreement([1, 2, 3, 4], XML_AGREEMENT_1)
#        self._set_company([1, 2, 3, 4], XML_COMPANY_A)
#        self.env.ref(XML_AGREEMENT_1).holding_invoice_generated_by = 'holding'
#        with self.assertRaises(UserError) as error:
#            self._start_scenario([1, 2, 3, 4], [1, 2])
#        self.assertIn('must be invoiced from the holding company',
#                      error.exception.message)
