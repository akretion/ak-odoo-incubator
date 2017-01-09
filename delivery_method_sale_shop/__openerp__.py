# coding: utf-8
# @author Raphael Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Delivery methods on ShopsAccounts',
    'version': '9.0.0.0.0',
    'author': 'Akretion',
    'summary': 'Set a delivery method for each shop',
    'maintainer': 'Akretion, Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'depends': [
        'keychain',
        'delivery_roulier',
        'sale_shop',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'view/sale_view.xml',
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
