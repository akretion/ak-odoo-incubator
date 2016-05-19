# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'sale_order_lot_mrp',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """
    """,
    'author': 'Akretion',
    'website': '',
    'depends': [
        'mrp_production_note',
        'sale_order_lot_generator',
    ],
    'data': [
        'mrp_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
