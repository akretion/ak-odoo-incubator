# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SaleMakeInvoice(models.TransientModel):
    _inherit = 'sale.make.invoice'

    error = fields.Text(readonly=True, default=lambda s: s._compute_error())
    agreement_id = fields.Many2one(
        comodel_name='agreement', string=u"Agreement", readonly=True,
        default=lambda s: s._compute_agree())

    def _get_info(self):
        if not self.env.context.get('active_ids'):
            return {}
        sales = self.env['sale.order'].browse(self.env.context['active_ids'])
        # TODO put as defaultdict
        agrees = {}
        for sale in sales:
            if agrees.get(sale.agreement_id):
                agrees[sale.agreement_id] |= sale
            else:
                agrees[sale.agreement_id] = sale
        for agree, sales in agrees.items():
            if agree.holding_company_id:
                if len(agrees) != 1:
                    return {
                        'error': _(
                            'Holding Invoice must be invoiced per agree')}
                if agree.holding_invoice_generated_by == 'holding':
                    user = self.env['res.users'].browse(self.env.uid)
                    if user.company_id == agree.holding_company_id:
                        return {
                            'error': (
                                _('The sale order %s must be invoiced from '
                                  'the holding company')
                                % (', '.join(sales.mapped('name'))))}
                else:
                    not_invoiceable = self.env['sale.order'].browse()
                    for sale in sales:
                        if sale.invoice_state != 'to invoice':
                            not_invoiceable |= sale
                    if not_invoiceable:
                        return {
                            'error': (
                                _("The sale order %s can't be invoiced")
                                % (', '.join(not_invoiceable.mapped('name'))))}
                return {'agree': agree}
        return {}

    def _compute_error(self):
        msg = self._get_info()
        return msg.get('error')

    def _compute_agree(self):
        msg = self._get_info()
        return msg.get('agree') or self.env['agreement'].browse()

    @api.multi
    def make_invoices(self):
        self.ensure_one()
        if self.error:
            raise UserError(self.error)
        if self.agreement_id:
            domain = [('id', 'in', self.env.context['active_ids'])]
            invoices = self.env['holding.invoicing'].suspend_security() \
                ._generate_invoice(domain, date_invoice=self.invoice_date)
            if invoices:
                return {
                    'name': _("Invoice Generated"),
                    'res_model': 'account.invoice',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': self.env.ref('account.action_invoice_tree1').id,
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', invoices.ids)]
                }
            return True
        else:
            return super(SaleMakeInvoice, self).make_invoices()
