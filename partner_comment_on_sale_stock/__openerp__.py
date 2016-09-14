# coding: utf-8
# © 2016 David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Partner comment on Sale Stock',
    'summary': 'Display partner comment field on sales and picking',
    'version': '8.0.0.0.1',
    'category': 'Stock',
    'author': 'Akretion',
    'description': """
Display partner comment field on sales and picking
""",
    'depends': [
        'sale',
        'stock',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
