# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import SavepointCase
from datetime import datetime
from openerp.addons.connector.tests.common import mock_job_delay_to_direct

CHILD_JOB_PATH = (
    'openerp.addons.multi_company_holding_invoicing'
    '.models.invoice.generate_child_invoice_job')

XML_COMPANY_A = 'multi_company_holding_invoicing.child_company_a'
XML_COMPANY_B = 'multi_company_holding_invoicing.child_company_b'
XML_COMPANY_HOLDING = 'base.main_company'
XML_SECTION_1 = 'multi_company_holding_invoicing.section_market_1'
XML_SECTION_2 = 'multi_company_holding_invoicing.section_market_2'
XML_PARTNER_ID = 'base.res_partner_2'
XML_PRODUCT = 'multi_company_holding_invoicing.holding_product'
XML_ROYALTY_PRODUCT = 'multi_company_holding_invoicing.holding_royalty_product'


class CommonInvoicing(SavepointCase):

    @classmethod
    def _get_account_id(cls, company, name):
        return cls.env['account.account'].search([
            ('name', 'ilike', 'Product Sales'),
            ('company_id', '=', company.id)
            ])[0].id

    @classmethod
    def _configure_product_and_taxe(cls):
        env = cls.env
        tax_obj = env['account.tax']
        sale_tax_ids = []
        purchase_tax_ids = []
        holding_product = env.ref(XML_PRODUCT)
        holding_royalty_product = env.ref(XML_ROYALTY_PRODUCT)
        for company in [cls.company_a, cls.company_b, cls.company_holding]:
            # configure accounts
            account_vals = {
                'property_account_income': cls._get_account_id(company, 'Product Sales'),
                'property_account_expense': cls._get_account_id(company, 'Expenses'),
                }
            holding_product.with_context(force_company=company.id).write(account_vals)
            holding_royalty_product.with_context(force_company=company.id).write(account_vals)

            # configure taxes
            sale_tax_a = tax_obj.create({
                'name': 'Sale tax A',
                'amount': 0.05,
                'type_tax_use': 'sale',
                'amount_type': 'percent',
                'company_id': company.id,
                'account_id': cls._get_account_id(company, 'Tax Received'),
                })
            sale_tax_ids.append(sale_tax_a.id)
            sale_tax_b = tax_obj.create({
                'name': 'Sale tax B',
                'amount': 0.10,
                'type_tax_use': 'sale',
                'amount_type': 'percent',
                'company_id': company.id,
                'account_id': cls._get_account_id(company, 'Tax Received'),
                })
            purchase_tax_a = tax_obj.create({
                'name': 'Purchase tax A',
                'amount': 0.05,
                'type_tax_use': 'purchase',
                'amount_type': 'percent',
                'company_id': company.id,
                'account_id': cls._get_account_id(company, 'Tax Paid'),
                })
            purchase_tax_ids.append(purchase_tax_a.id)
            purchase_tax_b = tax_obj.create({
                'name': 'Purchase tax B',
                'amount': 0.10,
                'type_tax_use': 'purchase',
                'amount_type': 'percent',
                'company_id': company.id,
                'account_id': cls._get_account_id(company, 'Tax Paid'),
                })
            env['account.fiscal.position'].create({
                'name': 'holding-test',
                'company_id': company.id,
                'tax_ids': [
                    (0, 0, {'tax_src_id': sale_tax_a.id, 'tax_dest_id': sale_tax_b.id}),
                    (0, 0, {'tax_src_id': purchase_tax_a.id, 'tax_dest_id': purchase_tax_b.id}),
                    ]
                })
        vals = {
            'taxes_id': [(6, 0, sale_tax_ids)],
            'supplier_taxes_id': [(6, 0, purchase_tax_ids)],
            }
        holding_product.write(vals)
        holding_royalty_product.write(vals)

    @classmethod
    def setUpClass(cls):
        super(CommonInvoicing, cls).setUpClass()
        # tests are called before register_hook
        # register suspend_security hook
        cls.env['ir.rule']._register_hook()
        cls.company_a = cls.env.ref(XML_COMPANY_A)
        cls.company_b = cls.env.ref(XML_COMPANY_B)
        cls.company_holding = cls.env.ref(XML_COMPANY_HOLDING)
        cls._configure_product_and_taxe()

    @classmethod
    def _get_sales(cls, xml_ids):
        sales = cls.env['sale.order'].browse(False)
        for xml_id in xml_ids:
            sale = cls.env.ref(
                'multi_company_holding_invoicing.sale_order_%s' % xml_id)
            sales |= sale
        return sales

    @classmethod
    def _validate_and_deliver_sale(cls, xml_ids):
        sales = cls._get_sales(xml_ids)
        for sale in sales:
            sale.action_button_confirm()
            for picking in sale.picking_ids:
                picking.force_assign()
                picking.do_transfer()
        return sales

    def _set_partner(self, sale_xml_ids, partner_xml_id):
        partner = self.env.ref(partner_xml_id)
        sales = self._get_sales(sale_xml_ids)
        sales.write({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            })

    def _set_company(self, sale_xml_ids, company_xml_id):
        company = self.env.ref(company_xml_id)
        sales = self._get_sales(sale_xml_ids)
        sales.write({'company_id': company.id})

    def _set_section(self, sale_xml_ids, section_xml_id):
        section = self.env.ref(section_xml_id)
        sales = self._get_sales(sale_xml_ids)
        sales.write({'section_id': section.id})

    def _generate_holding_invoice_from_section(self, section_xml_id):
        date_invoice = datetime.today()
        wizard = self.env['wizard.holding.invoicing'].create({
            'section_id': self.ref(section_xml_id),
            'date_invoice': date_invoice,
            })
        res = wizard.create_invoice()
        invoices = self.env['account.invoice'].browse(res['domain'][0][2])
        return invoices

    def _check_number_of_invoice(self, invoices, number):
        self.assertEqual(
            len(invoices), 1,
            msg="Only one invoice should have been created, %s created"
                % len(invoices))

    def _check_invoiced_sale_order(self, invoice, sales):
        self.assertEqual(
            sales,
            invoice.holding_sale_ids,
            msg="Expected sale order to be invoiced %s found %s"
                % (', '.join(sales.mapped('name')),
                   ', '.join(invoice.holding_sale_ids.mapped('name'))))

    def _check_child_invoice(self, invoice):
        company2sale = {}
        for sale in invoice.holding_sale_ids:
            if not company2sale.get(sale.company_id.id):
                company2sale[sale.company_id.id] = sale
            else:
                company2sale[sale.company_id.id] |= sale
        for child in invoice.child_invoice_ids:
            expected_sales = company2sale.get(child.company_id.id)
            if expected_sales:
                expected_sales_name = ', '.join(expected_sales.mapped('name'))
            else:
                expected_sales_name = ''
            if child.sale_ids:
                found_sales_name = ', '.join(child.sale_ids.mapped('name'))
            else:
                found_sales_name = ''
            self.assertEqual(
                child.sale_ids, expected_sales,
                msg="The child invoice generated is not linked to the "
                    "expected sale order. Found %s, expected %s"
                    % (found_sales_name, expected_sales_name))

    def _check_child_invoice_partner(self, invoice):
        holding_partner = invoice.company_id.partner_id
        for child in invoice.child_invoice_ids:
            self.assertEqual(
                child.partner_id.id,
                holding_partner.id,
                msg="The partner invoiced is not correct excepted %s get %s"
                    % (holding_partner.name, child.partner_id.name))

    def _check_sale_state(self, sales, expected_state):
        for sale in sales:
            self.assertEqual(
                sale.invoice_state, expected_state,
                msg="Invoice state is '%s' indeed of '%s'"
                    % (sale.invoice_state, expected_state))


class CommonGenerateInvoice(CommonInvoicing):

    @classmethod
    def setUpClass(cls):
        super(CommonGenerateInvoice, cls).setUpClass()
        # Validate the sale order (sale_xml_ids) and check the state
        cls._validate_and_deliver_sale([1, 2, 3, 4])
