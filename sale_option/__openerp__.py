# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale option',
    'version': '0.0.1',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'sale_order_lot_generator',
        'sale_order_lot_mrp',
    ],
    'data': [
        'sale_view.xml',
        'mrp_view.xml',
        'config.yml',
        'install.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/product_demo.xml',
    ],
    'installable': True,
    'application': False,
}
