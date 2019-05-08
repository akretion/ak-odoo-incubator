# © 2019 Florian da Costa @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Automatic Supplier Delay',
    'summary': 'Automatically compute supplier delays and po planned date',
    'license': 'AGPL-3',
    'version': '12.0.0.0.0',
    'author': 'Akretion',
    'maintainer': 'Akretion',
    'category': 'purchase',
    'depends': [
        'purchase_stock',
    ],
    'data': [
        'views/res_partner.xml',
        'views/res_config_settings_view.xml',
    ],
    'website': 'http://www.akretion.com/',
    'installable': True,
}
