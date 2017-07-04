# coding: utf-8
# © 2017 Chafique DELLI @ Akretion <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Stock Default Warehouse by Company",
    'summary': 'Add in the company, default warehouse for outgoing shipments '
               'and incoming shipments',
    'author': "Akretion",
    'website': "http://www.akretion.com",
    'category': 'Tools',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'sale_stock',
        'purchase',
    ],
    'data': [
        'views/company_view.xml',
    ],
}
