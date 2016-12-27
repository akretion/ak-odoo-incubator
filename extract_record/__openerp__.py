# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Extract Record',
    'version': '0.5',
    'author': 'Akretion',
    'maintener': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'delivery',
    ],
    'description': """

Feature
-------------
Allow to extract records from one db to create equivalent ones in other db

Contributors
------------
* David BEAL <david.beal@akretion.com>

""",
    'website': 'http://www.akretion.com/',
    'data': [
        'stock_view.xml',
    ],
    'license': 'AGPL-3',
    'tests': [],
    'installable': True,
}
