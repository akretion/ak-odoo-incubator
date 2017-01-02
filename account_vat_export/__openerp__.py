# coding: utf-8
# © 2016 Benoît GUILLOT @ Akretion <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account VAT Export',
    'version': '1.0',
    'author': 'Akretion',
    'summary': "VAT Export",
    'maintainer': 'Akretion',
    'category': 'Accounting',
    'depends': [
        'account_invoice_shipping_address',
    ],
    'description': """



Contributors
------------

* Benoît GUILLOT @ Akretion <benoit.guillot@akretion.com>


    """,
    'website': 'http://www.akretion.com/',
    'data': [
        'wizard/vat_export_view.xml',
    ],
    'tests': [],
    'demo': [
    ],
    'installable': True,
    'license': 'AGPL-3',
}
