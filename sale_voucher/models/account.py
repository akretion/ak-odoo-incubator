# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm
from openerp.tools.translate import _


class AccountAccount(orm.Model):
    _inherit = 'account.account'

    _columns = {
        'voucher_account': fields.boolean(
            'Voucher Account',
            help=('Voucher Account for customer credit. The balance of the '
                  'Account must positive and the partner on line is '
                  'required')),
    }


class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'

    def _check_positif_balance(self, cr, uid, ids, context=None):
        lines = self.read_group(cr, uid, [
            ('account_id.voucher_account', 'in', True),
            ('id', 'in', ids),
            ], ['partner_id'], ['partner_id'],
            context=context)
        partner_obj = self.pool['res.partner']
        p_ids = [l['partner_id'][0] for l in lines]
        for partner in partner_obj.browse(cr, uid, p_ids, context=context):
            if partner.voucher_amount < 0:
                raise orm.except_orm(
                    _('User Error'),
                    _("The customer %s do not have enought customer voucher")
                    % partner.name)
        return True

    _constraints = [
        (_check_positif_balance, 'Error', ['account_id', 'debit', 'credit'])
    ]
