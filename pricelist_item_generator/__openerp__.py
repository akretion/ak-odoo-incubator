# coding: utf-8
# © 2016 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Pricelist Item Generator',
    'version': '8.0.0.0.1',
    'category': '',
    'sequence': 10,
    'summary': "Create/Update Pricelist Item in a massive way",
    'description': """
Multiple pricelist items creation at once based on templates

CAREFUL : if your are not SUPER ADMIN, you must in check 'Use pricelists to
adapt your price per customers' in
'Settings > Configuration > Sales > Customer Features' before installation.
If you are SUPER ADMIN, there is nothing to do

Settings:
- define an appropriate 'Next execution date' 'Scheduled action'
according to your local time for 'Pricelist builder'

Icon images comes from http://icons8.com/

    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale',
        ],
    'data': [
        'pricelist_view.xml',
        'setting_view.xml',
        'security/ir.model.access.csv',
        'cron_data.xml',
    ],
    'demo': [
        'demo/pricelist.item.generator.csv',
        'demo/pricelist.product.condition.csv',
        'demo/pricelist.item.template.csv',
    ],
    'installable': True,
    'images': [
    ],
}
