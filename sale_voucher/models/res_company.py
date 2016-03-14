# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'voucher_account_id': fields.many2one(
            'account.account', string='Voucher Account')
    }
