# coding: utf-8
# @author Raphael Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Delivery accounts on Shops',
    'version': '9.0.0.0.0',
    'author': 'Akretion',
    'summary': 'Set a delivery account for each shop',
    'maintainer': 'Akretion, Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'depends': [
        'keychain',
        'delivery_roulier',
        'sale_shop',
        'sale_shop_keychain',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
    ],
    'demo': [
    ],
    'external_dependencies': {
    },
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
