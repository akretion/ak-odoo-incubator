# -*- coding: utf-8 -*-
# © 2018 Akretion <https://www.akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice Pricelist Stock - Account',
    'summary': 'Set pricelist from PO in invoice created from picking.',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://www.akretion.com',
    'category': 'Warehouse Management',
    'version': '8.0.1.0.0',
    'depends': [
        'account_invoice_pricelist_purchase',
        'stock',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
