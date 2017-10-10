# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Voucher',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module introduce the concept of voucher
    (gift voucher). When you do a refund you can pay it with a voucher so
    your customer can use it to pay a new sale order.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['sale_payment_method'],
    'data': [
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/account_view.xml',
        'views/voucher_expiration_view.xml',
        'wizard/voucher_reverse_view.xml',
        'data.xml',
        'security/rule.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
}
