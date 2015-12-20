# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Global Discount Rules',
    'version': '0.8',
    'category': 'Sales',
    'sequence': 10,
    'summary': "Define discount rules",
    'description': """
Define discount rules
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale',
        ],
    'data': [
        'price_rule_view.xml',
        'sale_view.xml',
        'setting_view.xml',
        'misc_data.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
}
