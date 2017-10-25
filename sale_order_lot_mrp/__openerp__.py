# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Order Lot Mrp',
    'version': '8.0.0.1.1',
    'category': 'Manufacturing',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'depends': [
        'mrp_production_note',
        'sale_order_lot_generator',
    ],
    'data': [
        'views/mrp_view.xml',
    ],
    'demo': [
        'demo/product_demo.xml',
        'demo/config.yml',
    ],
    'installable': True,
}
