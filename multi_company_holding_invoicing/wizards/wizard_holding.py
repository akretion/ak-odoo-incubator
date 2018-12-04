# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InvoiceWizard(models.TransientModel):
    _name = "wizard.holding.invoicing"

    invoice_date = fields.Date(
        'Invoice Date',
        required=True,
        default=fields.Datetime.now)
    agreement_id = fields.Many2one(
        comodel_name='agreement', string=u"Agreement", required=True)

    def _get_invoice_domain(self):
        self.ensure_one()
        return [
            ('agreement_id', '=', self.agreement_id.id),
            ('holding_invoice_state', '=', 'invoiceable'),
            ('holding_invoice_id', '=', False),
            ('company_id', '!=', self.agreement_id.holding_company_id.id)
            ]

    def _return_open_action(self, invoices):
        action = self.env.ref('account.action_invoice_tree').read()[0]
        action.update({
            'name': _("Invoice Generated"),
            'target': 'current',
            'domain': [('id', 'in', invoices.ids)]
        })
        return action

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        domain = self._get_invoice_domain()
        invoices = self.env['holding.invoicing']._generate_invoice(
            domain, invoice_date=self.invoice_date)
        if invoices:
            return self._return_open_action(invoices)
        else:
            raise UserError(_('There is no invoice to generate'))
