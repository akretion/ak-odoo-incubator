# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'voucher_account_id': fields.many2one(
            'account.account', string='Voucher Account'),
        'voucher_reverse_account_id': fields.many2one(
            'account.account', string='Voucher Expiration Account'),
        'voucher_validity_time': fields.integer(
            'Voucher validity time (months)'),
        'voucher_warning_time': fields.integer(
            'Voucher warning time (days)',
            help='It defines the date when the partner will be notified that '
            'his voucher will expire. it is the number of days before '
            'the expiration date.')

    }
