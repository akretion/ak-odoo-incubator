# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def _get_customer_voucher_amount(self, cr, uid, ids, field_name, args,
                                     context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        datas = self.pool['account.move.line'].read_group(cr, uid, [
            ('account_id', '=', user.company_id.voucher_account_id.id),
            ('partner_id', 'in', ids),
            ], ['partner_id', 'debit', 'credit'], ['partner_id'],
            context=context)
        datas = {data['partner_id'][0]: data for data in datas}
        result = {}
        for partner_id in ids:
            if datas.get(partner_id):
                result[partner_id] = datas[partner_id]['credit']\
                    - datas[partner_id]['debit']
            else:
                result[partner_id] = 0
        return result

    _columns = {
        'voucher_amount': fields.function(
            _get_customer_voucher_amount,
            type='float',
            string='Voucher Amount',
            digits_compute=dp.get_precision('Account'))
        }
