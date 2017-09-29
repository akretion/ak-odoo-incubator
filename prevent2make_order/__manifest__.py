# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Prevent to Make Orders',
    'summary': 'Avoid to create test data in sale, purchase',
    'description': """
        Forbide to create these objects: sale.order, purchase.order,
        stock.picking, account.invoice
        by raising an alert to the user on recording.
        This module is only useful before to reach 'production' step of
        ERP implementation project.
        """,
    'version': '8.0.1.0.0',
    'author': 'Akretion',
    'maintainer': 'Akretion',
    'category': 'sale',
    'depends': [
        'sale_stock',
        'purchase',
        'account',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
    ],
    'installable': False,
    'license': 'AGPL-3',
}
