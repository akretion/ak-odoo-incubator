# coding: utf-8
# © 2015 David BEAL @ Akretion
# © 2019 Mourad EL HADJ MIMOUNE @ Akretion
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
        'version': '12.0.1.0.0',
    'author': 'Akretion',
    'maintainer': 'Akretion',
    'category': 'tools',
    'depends': [
        'base',
        'base_setup',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'views/config_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
