# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _get_info(self):
        if not self._context.get('active_ids'):
            return {}
        sales = self.env['sale.order'].browse(self._context['active_ids'])
        agreements = {}
        for sale in sales:
            if agreements.get(sale.agreement_id):
                agreements[sale.agreement_id] |= sale
            else:
                agreements[sale.agreement_id] = sale
        for agreement, sales in agreements.items():
            if agreement.holding_company_id:
                if len(agreements) != 1:
                    return {
                        'error':
                        _('Holding Invoice must be invoiced per agreement')}
                if agreement.holding_invoice_generated_by == 'holding':
                    user = self.env['res.users'].browse(self._uid)
                    if user.company_id == agreement.holding_company_id:
                        return {
                            'error': (
                                _('The sale order %s must be invoiced from '
                                  'the holding company')
                                % (', '.join(sales.mapped('name'))))}
                else:
                    not_invoiceable = self.env['sale.order'].browse(False)
                    for sale in sales:
                        if sale.invoice_state != 'invoiceable':
                            not_invoiceable |= sale
                    if not_invoiceable:
                        return {
                            'error': (
                                _('The sale order %s can not be invoiced')
                                % (', '.join(not_invoiceable.mapped('name'))))}
                return {'agreement': agreement,
                        'agreement_holding': agreement.holding_company_id}
        return {}

    def _compute_error(self):
        msg = self._get_info()
        return msg.get('error')

    def _compute_agreement(self):
        msg = self._get_info()
        if msg.get('agreement'):
            return msg['agreement']
        else:
            return self.env['agreement'].browse(False)

    def _compute_agreement_holding(self):
        msg = self._get_info()
        if msg.get('agreement_holding'):
            return msg['agreement_holding']
        else:
            return self.env['res.company'].browse(False)

    error = fields.Text(default=_compute_error, readonly=True)
    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Sale Agreement',
        default=_compute_agreement,
        readonly=True)
    agreement_holding_id = fields.Many2one(
        comodel_name='res.company',
        string='Holding Company',
        default=_compute_agreement_holding,
        readonly=True)
    invoice_date = fields.Date(
        string='Invoice Date',
        required=True,
        default=fields.Datetime.now)

    @api.multi
    def create_invoices(self):
        self.ensure_one()
        if self.error:
            raise UserError(self.error)
        if self.agreement_id and self.agreement_holding_id:
            domain = [('id', 'in', self.env.context.get('active_ids', []))]
            invoices = self.env['holding.invoicing'].suspend_security()\
                ._generate_invoice(domain, invoice_date=self.invoice_date)
            if invoices:
                return self.env['wizard.holding.invoicing']\
                    ._return_open_action(invoices)
            else:
                raise UserError(_('There is no invoice to generate'))
        return super(SaleAdvancePaymentInv, self).create_invoices()
