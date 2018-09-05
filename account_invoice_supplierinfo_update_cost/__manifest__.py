# -*- coding: utf-8 -*-
# © 2018 Pierrick BRUN @ Akretion
# @author: Pierrick Brun (pierrick.brun@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice - Supplier Info Update Cost',
    'summary': 'Make the account_invoice_supplierinfo_update'
               'module optionnaly update the cost as well',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'website': 'http://akretion.com',
    'author':
        'Akretion,'
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'account_invoice_supplierinfo_update',
    ],
    'data': [
        'wizard/wizard_update_invoice_supplierinfo.xml'
    ],
}
