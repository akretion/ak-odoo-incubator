# -*- coding: utf-8 -*-
# © 2018 Akretion <https://www.akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice Pricelist - Purchase',
    'summary': 'Module to fill pricelist from purchase order in invoice.',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://www.akretion.com',
    'category': 'Purchase Management',
    'version': '8.0.1.0.0',
    'depends': [
        'account_invoice_pricelist',
        'purchase',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
