# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Reserve Location',
    'summary': 'Allow to feed picking locations from reserve locations',
    'version': '8.0.1.0.0',
    'author': 'Akretion',
    'description': """
- overstock implementation: exchange between: picking and reserve locations
-
""",
    'depends': [
        'stock',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'views/stock_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
