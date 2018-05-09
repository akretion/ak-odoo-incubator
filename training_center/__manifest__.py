# coding: utf-8
# © 2018 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Training Center",
    'author': " Akretion",
    'website': "https://www.akretion.com",
    'category': 'Employees',
    'summary': '',
    'version': '10.0.0.1',
    'depends': [
        'base_company_extension',
        'sale_usability',
        'report_py3o',
    ],
    'data': [
        'views/training_view.xml',
        'views/company_view.xml',
        'report/report.xml',
        'security/training_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'license': 'AGPL-3',
}
