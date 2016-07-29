# -*- encoding: utf-8 -*-
#################################################################################
#
#    account_journal_sale_refund_link for OpenERP
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#                  2014 Akretion Chafique DELLI <chafique.delli@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from openerp.osv import orm


class account_invoice_refund(orm.TransientModel):

    _inherit = "account.invoice.refund"

    def _get_journal(self, cr, uid, context=None):
        invoice_id = context.get('invoice_ids', [context['active_id']])[0]
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        refund_journal_id = invoice.journal_id.refund_journal_id
        if refund_journal_id:
            return refund_journal_id.id
        else:
            return super(account_invoice_refund, self)._get_journal(cr, uid, context)

    _defaults = {
    'journal_id': _get_journal,
    }
