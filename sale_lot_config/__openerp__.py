# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Lot Config',
    'version': '9.0.0.1.1',
    'category': 'Sale',
    'description': """
Add config on lot from sale order line config
    """,
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'depends': [
        'sale_order_lot_generator',
    ],
    'data': [
        'sale_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
