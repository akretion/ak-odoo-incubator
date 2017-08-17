# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    @api.model
    def _get_journal(self):
        # compatibility with crm_claim_rma module
        invoice_id = self._context.get(
            'invoice_ids', [self._context['active_id']])[0]
        invoice = self.env['account.invoice'].browse(invoice_id)
        refund_journal_id = invoice.journal_id.refund_journal_id
        if refund_journal_id:
            return refund_journal_id.id
        else:
            return super(AccountInvoiceRefund, self)._get_journal()

    journal_id = fields.Many2one(default=_get_journal)
