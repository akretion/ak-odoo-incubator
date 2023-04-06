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
        'base_delivery_carrier_label',
        'proxy_action',
    ],
    'data': [
        'views/stock_picking.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
}
