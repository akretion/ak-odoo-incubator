# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BaseHoldingInvoicing(models.AbstractModel):
    _name = 'base.holding.invoicing'

    @api.model
    def _get_invoice_line_data(self, data):
        if self.env.context.get('agree_group_by') == 'none':
            return [data]
        else:
            read_fields, groupby = self._get_group_fields()
            read_fields += ['name', 'client_order_ref']
            groupby += ['name', 'client_order_ref']
            return self.env['sale.order'].read_group(
                data['__domain'], read_fields, groupby, lazy=False)

    @api.model
    def _get_accounting_value_from_product(self, data_line, product):
        company = self.env['res.company'].browse(
            self.env.context['force_company'])
        if self.env.context.get('agree_group_by') == 'none':
            name = product.name
        else:
            name = '%s - %s' % (
                data_line['name'], data_line.get('client_order_ref', ''))
        # get invoice line data from product onchange
        invoice = self.env['account.invoice'].browse(
            data_line.get('invoice_id'))
        line_data = {
            'product_id': product.id,
            'uom_id': product.uom_id.id,
            'name': '',
            'company_id': company.id,
            'partner_id': invoice.partner_id.id,
            'invoice_id': data_line.get('invoice_id'),
        }
        line_data = self.env['account.invoice.line'].play_onchanges(
            line_data, ['product_id'])
        if not line_data.get('account_id'):
            raise UserError(_(
                'Please define %s account in the product "%s" for this '
                'company: "%s" (id:%d).')
                % (self.env.ref('account.data_account_type_revenue').name,
                   product.name, company.name, company.id))
        return {
            'name': name,
            'product_id': product.id or False,
            'uom_id': product.uom_id.id,
            'invoice_line_tax_ids': line_data.get('invoice_line_tax_ids', []),
            'account_id': line_data.get('account_id', False),
        }

    @api.model
    def _prepare_invoice_line(self, data_line):
        agree = self.env['agreement'].browse(data_line['agreement_id'][0])
        vals = self._get_accounting_value_from_product(
            data_line, agree.holding_product_id)
        vals.update({
            'price_unit': data_line['amount_untaxed'],
            'quantity': data_line.get('quantity', 1),
        })
        return vals

    @api.model
    def _prepare_invoice(self, data):
        # get default from native method _prepare_invoice
        # use first sale order as partner and agreement are the same
        sale = self.env['sale.order'].search(data['__domain'], limit=1)
        vals = sale._prepare_invoice()
        vals.update({
            'origin': _('Holding Invoice'),
            'company_id': self.env.context['force_company'],
            'user_id': self.env.uid,
        })
        ## Remove fiscal position from vals
        ## Because fiscal position in vals is not that of the 'force_company'
        #if vals.get('fiscal_position'):
        #    vals['fiscal_position'] = False
        # Remove partner shipping from vals
        # Because there are potentially several delivery addresses
        if vals.get('partner_shipping_id'):
            vals['partner_shipping_id'] = False
        # Find the journal in the holding company
        # when invoice created from sale wizard
        journal = self.env['account.journal'].browse(
            vals.get('journal_id', False))
        if journal.company_id.id != vals['company_id']:
            new_journal = self.env['account.journal'].search([
                ('type', '=', 'sale'),
                ('company_id', '=', vals['company_id'])
            ], limit=1)
            vals['journal_id'] = new_journal.id
        return vals

    @api.model
    def _get_group_fields(self):
        return NotImplemented

    @api.model
    def _get_invoice_data(self, domain):
        read_fields, groupby = self._get_group_fields()
        return self.env['sale.order'].read_group(
            domain, read_fields, groupby, lazy=False)

    @api.model
    def _get_company_invoice(self, data):
        return NotImplemented

    @api.model
    def _link_sale_order(self, invoice, sales):
        return NotImplemented

    @api.model
    def _link_sale_order_line(self, invoice_lines, sale_lines):
        return NotImplemented

    @api.model
    def _create_inv_lines(self, val_lines):
        inv_line_obj = self.env['account.invoice.line']
        lines = inv_line_obj.browse(False)
        for val_line in val_lines:
            lines |= inv_line_obj.create(val_line)
        return lines

    @api.model
    def _generate_invoice(self, domain, invoice_date=None):
        self = self.suspend_security()
        invoices = self.env['account.invoice'].browse(False)
        _logger.debug('Retrieve data for generating the invoice')
        for data in self._get_invoice_data(domain):
            company = self._get_company_invoice(data)
            agree = self.env['agreement'].browse(data['agreement_id'][0])
            # add company and agreement info in the context
            loc_self = self.with_context(
                force_company=company.id,
                invoice_date=invoice_date,
                agreement_id=agree.id,
                agree_group_by=agree.holding_invoice_group_by)
            _logger.debug('Prepare vals for holding invoice')
            invoice_vals = loc_self._prepare_invoice(data)
            invoice_vals['date_invoice'] = invoice_date
            _logger.debug('Generate the holding invoice')
            invoice = loc_self.env['account.invoice'].create(invoice_vals)
            _logger.debug('Link the invoice with the sale order')
            sales = self.env['sale.order'].search(data['__domain'])
            self._link_sale_order(invoice, sales)
            data_lines = loc_self._get_invoice_line_data(data)
            val_lines = []
            for data_line in data_lines:
                data_line.update({'invoice_id': invoice.id})
                val_lines.append(loc_self._prepare_invoice_line(data_line))
            invoice_lines = loc_self._create_inv_lines(val_lines)
            _logger.debug('Link the invoice line with the sale order line')
            sale_lines = self.env['sale.order.line'].search([
                ('order_id', 'in', sales.ids)])
            self._link_sale_order_line(invoice_lines, sale_lines)
            invoice.update({'invoice_line_ids': [(6, 0, invoice_lines.ids)]})
            invoice.compute_taxes()
            invoices |= invoice
        return invoices


class HoldingInvoicing(models.TransientModel):
    _inherit = 'base.holding.invoicing'
    _name = 'holding.invoicing'

    @api.model
    def _get_group_fields(self):
        return [
            ['partner_invoice_id', 'agreement_id', 'amount_untaxed'],
            ['partner_invoice_id', 'agreement_id'],
        ]

    @api.model
    def _get_company_invoice(self, data):
        agree = self.env['agreement'].browse(
            data['agreement_id'][0])
        return agree.holding_company_id

    @api.model
    def _link_sale_order(self, invoice, sales):
        self._cr.execute("""UPDATE sale_order
            SET holding_invoice_id=%s, holding_invoice_state='pending'
            WHERE id in %s""", (invoice.id, tuple(sales.ids)))
        invoice.invalidate_cache()


class ChildInvoicing(models.TransientModel):
    _inherit = 'base.holding.invoicing'
    _name = 'child.invoicing'

    @api.model
    def _get_company_invoice(self, data):
        return self.env['res.company'].browse(data['company_id'][0])

    @api.model
    def _link_sale_order_line(self, invoice_lines, sale_lines):
        for sale_line in sale_lines:
            for invoice_line in invoice_lines:
                self._cr.execute("""INSERT INTO sale_order_line_invoice_rel (
                    invoice_line_id, order_line_id)
                    VALUES (%s, %s)""", (invoice_line.id, sale_line.id))
                invoice_line.invalidate_cache()

    @api.model
    def _get_invoice_line_data(self, data):
        agree = self.env['agreement'].browse(
            data['agreement_id'][0])
        data_lines = super(ChildInvoicing, self)._get_invoice_line_data(data)
        data_lines.append({
            'name': 'royalty',
            'amount_untaxed': data['amount_untaxed'],
            'quantity': - agree.holding_discount / 100.,
            'sale_line_ids': [],
            'agreement_id': [agree.id],
        })
        return data_lines

    @api.model
    def _prepare_invoice_line(self, data_line):
        # add child_invoicing info in the context
        # used in_get_invoice_qty method in sale order line
        self.env.context = dict(self.env.context).copy()
        self.env.context.update({'child_invoicing': True})
        val_line = super(ChildInvoicing, self).\
            _prepare_invoice_line(data_line)
        # TODO the code is too complicated
        # we should simplify the _get_invoice_line_data
        # and _prepare_invoice_line to avoid this kind of hack
        if data_line.get('name') == 'royalty':
            agree = self.env['agreement'].browse(
                data_line['agreement_id'][0])
            val_line.update(self._get_accounting_value_from_product(
                data_line,
                agree.holding_royalty_product_id))
            val_line['name'] = agree.holding_royalty_product_id.name
        return val_line

    @api.model
    def _prepare_invoice(self, data):
        vals = super(ChildInvoicing, self)._prepare_invoice(data)
        sale = self.env['sale.order'].search(data['__domain'], limit=1)
        holding_invoice = sale.holding_invoice_id
        vals['origin'] = holding_invoice.name
        vals['partner_id'] = holding_invoice.company_id.partner_id.id
        agree = self.env['agreement'].browse(data['agreement_id'][0])
        if agree.journal_id:
            journal_id = agree.journal_id
        else:
            journal_id = self.env['account.invoice'].with_context(
                company_id=data['company_id'][0])._default_journal()
        if not journal_id:
            raise UserError(_(
                'Please define an accounting sale journal for the company %s.',
                data['company_id'][1]))
        vals['journal_id'] = journal_id.id
        partner_data = {
            'type': 'out_invoice',
            'partner_id': holding_invoice.company_id.partner_id.id,
            'company_id': self.env.context['force_company'],
        }
        partner_data = self.env['account.invoice'].play_onchanges(
            partner_data, ['partner_id'])
        vals['account_id'] = partner_data.get('account_id', False)
        return vals

    @api.model
    def _get_group_fields(self):
        return [
            ['partner_invoice_id', 'agreement_id',
             'company_id', 'amount_untaxed'],
            ['partner_invoice_id', 'agreement_id', 'company_id'],
        ]
