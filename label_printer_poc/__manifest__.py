# coding: utf-8
{
    'name': 'label printer poc',
    'version': '14.0.0.0.1',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'description': """
Toutes les dépendences du projet""",
    'depends': [
        'stock',
        'proxy_action',
        'base_delivery_carrier_label',
    ],
    'data': [
        'views/stock_picking.xml',
    ],
    'installable': True,
    'application': False,
}
