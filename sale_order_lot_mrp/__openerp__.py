# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'sale_order_lot_mrp',
    'version': '8.0.0.1.1',
    'category': 'Manufacturing',
    'description': """
Allow you to attach a lot in manufacturing order
that was defined by sale_order_lot_generator module
for all concerned products (Lot Generation Auto field)
Name of the MO is also based on sale name
    """,
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'depends': [
        'mrp_production_note',
        'sale_order_lot_generator',
    ],
    'data': [
        'mrp_view.xml',
    ],
    'demo': [
        'demo/product_demo.xml',
        'demo/config.yml',
    ],
    'installable': True,
}
