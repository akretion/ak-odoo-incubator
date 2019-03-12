# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Configuration Traceability Sale',
    'summary': 'Add minimal social features to sale/account base odoo objects',
    'license': 'AGPL-3',
    'version': '12.0.0.0.0',
    'author': 'Akretion',
    'maintainer': 'Akretion',
    'category': 'Social',
    'depends': [
        'mail',
        'sale',
    ],
    'data': [
        'views/account_view.xml',
    ],
    'website': 'http://www.akretion.com/',
    'installable': True,
}
