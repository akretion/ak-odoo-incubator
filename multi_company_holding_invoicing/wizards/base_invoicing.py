# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, api, _
import logging
_logger = logging.getLogger(__name__)


class BaseHoldingInvoicing(models.AbstractModel):
    _name = 'base.holding.invoicing'

    @api.model
    def _get_invoice_line_data(self, data):
        section = self.env['crm.case.section'].browse(data['section_id'][0])
        if section.holding_invoice_group_by == 'none':
            data['name'] = _('Global Invoice')
            return [data]
        else:
            read_fields, groupby = self._get_group_fields()
            read_fields.append('name')
            groupby.append('name')
            datas = self.env['sale.order'].read_group(
                data['__domain'], read_fields, groupby, lazy=False)
            return datas

    @api.model
    def _prepare_invoice_line(self, data_line):
        return {
            'name': data_line['name'],
            'price_unit': data_line['amount_total'],
            'quantity': data_line.get('quantity', 1),
            }

    @api.model
    def _prepare_invoice(self, data, lines):
        # get default from native method _prepare_invoice
        # use first sale order as partner and section are the same
        sale = self.env['sale.order'].search(data['__domain'], limit=1)
        vals = self.env['sale.order']._prepare_invoice(sale, lines.ids)
        vals.update({
            'origin': _('Holding Invoice'),
            'company_id': self._context['force_company'],
            'user_id': self._uid,
            })
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
    def _generate_invoice(self, domain, date_invoice=None):
        invoices = self.env['account.invoice'].browse(False)
        _logger.debug('Retrieve data for generating the invoice')
        for data in self._get_invoice_data(domain):
            company = self._get_company_invoice(data)

            # add company context in the self
            loc_self = self.with_context(
                force_company=company.id,
                invoice_date=date_invoice)

            inv_obj = loc_self.env['account.invoice']
            inv_line_obj = loc_self.env['account.invoice.line']

            _logger.debug('Prepare vals for holding invoice')
            lines = inv_line_obj.browse(False)
            data_lines = loc_self._get_invoice_line_data(data)
            for data_line in data_lines:
                val_line = loc_self._prepare_invoice_line(data_line)
                lines |= inv_line_obj.create(val_line)
            invoice_vals = loc_self._prepare_invoice(data, lines)
            _logger.debug('Generate the holding invoice')
            invoice = inv_obj.create(invoice_vals)
            invoice.button_reset_taxes()
            _logger.debug('Link the invoice with the sale order')
            sales = self.env['sale.order'].search(data['__domain'])
            self._link_sale_order(invoice, sales)
            invoices |= invoice
        return invoices


class HoldingInvoicing(models.TransientModel):
    _inherit = 'base.holding.invoicing'
    _name = 'holding.invoicing'

    @api.model
    def _get_group_fields(self):
        return [
            ['partner_invoice_id', 'section_id', 'amount_total'],
            ['partner_invoice_id', 'section_id'],
        ]

    @api.model
    def _get_company_invoice(self, data):
        section = self.env['crm.case.section'].browse(
            data['section_id'][0])
        return section.holding_company_id

    @api.model
    def _link_sale_order(self, invoice, sales):
        self._cr.execute("""UPDATE sale_order
            SET holding_invoice_id=%s, invoice_state='pending'
            WHERE id in %s""", (invoice.id, tuple(sales.ids)))
        invoice.invalidate_cache()


class ChildInvoicing(models.TransientModel):
    _inherit = 'base.holding.invoicing'
    _name = 'child.invoicing'

    @api.model
    def _get_company_invoice(self, data):
        return self.env['res.company'].browse(data['company_id'][0])

    @api.model
    def _link_sale_order(self, invoice, sales):
        sales.write({'invoice_ids': [(6, 0, [invoice.id])]})
        order_lines = self.env['sale.order.line'].search([
            ('order_id', 'in', sales.ids),
            ])
        order_lines._store_set_values(['invoiced'])
        # Dummy call to workflow, will not create another invoice
        # but bind the new invoice to the subflow
        sales.signal_workflow('manual_invoice')

    @api.model
    def _get_invoice_line_data(self, data):
        section = self.env['crm.case.section'].browse(
            data['section_id'][0])
        data_lines = super(ChildInvoicing, self)._get_invoice_line_data(data)
        data_lines.append({
            'name': _('Royalty'),
            'amount_total': data['amount_total'],
            'quantity': - section.holding_discount/100.,
            'sale_line_ids': [],
            })
        return data_lines

    @api.model
    def _prepare_invoice_line(self, data_line):
        val_line = super(ChildInvoicing, self).\
            _prepare_invoice_line(data_line)
        if data_line.get('__domain'):
            domain = []
            for arg in data_line['__domain']:
                if len(arg) == 3:
                    domain.append(('order_id.%s' % arg[0], arg[1], arg[2]))
            line_ids = self.env['sale.order.line'].search(domain).ids
            val_line['sale_line_ids'] = [(6, 0, line_ids)]
        return val_line

    @api.model
    def _prepare_invoice(self, data, lines):
        vals = super(ChildInvoicing, self)._prepare_invoice(data, lines)
        sale = self.env['sale.order'].search(data['__domain'], limit=1)
        vals['origin'] = sale.holding_invoice_id.name,
        return vals

    @api.model
    def _get_group_fields(self):
        return [
            ['partner_invoice_id', 'section_id', 'company_id', 'amount_total'],
            ['partner_invoice_id', 'section_id', 'company_id'],
        ]
