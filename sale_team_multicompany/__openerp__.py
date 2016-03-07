# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Team Multicompany',
    'summary': 'Add companies in sales team and '
    'filter the sales team from the company',
    'version': '8.0.0.1.0',
    'category': 'Sales Management',
    'website': 'http://akretion.com',
    'author': 'Akretion',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'sales_team',
    ],
    'data': [
        'sale_team_view.xml',
        'security/ir.rule.csv',
    ],
    'demo': [
        'demo/companies.csv',
        'demo/partners.csv',
        'demo/users.csv',
        'demo/sales_team.csv',
    ],
    'qweb': [
    ]
}
