# coding: utf-8
# © 2017 Benoît GUILLOT @ Akretion <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def _get_inv_from_partner(self, cr, uid, ids, context=None):
        return self.pool['account.invoice'].search(
            cr, uid, [('address_shipping_id', 'in', ids)], context=context)

    _columns = {
        'country_shipping_id': fields.related(
            'address_shipping_id',
            'country_id',
            type='many2one',
            relation='res.country',
            string='Country Shipping',
            store={
                'account.invoice': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['address_shipping_id'],
                    10),
                'res.partner': (
                    _get_inv_from_partner,
                    ['country_id'],
                    20)
                },
            ),
        }
