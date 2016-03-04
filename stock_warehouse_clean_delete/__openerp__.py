# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Clean Warehouse delete",
    'description': """
        Remote records related to a warehouse when you delete it (routes, sequences etc...)
    """,

    'author': "Akretion",
    'website': "http://www.akretion.com",

    # Categories can be used to filter modules in modules listing
    # Check <odoo>/addons/base/module/module_data.xml of the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],
    'data': [],

    'demo': [],

    'tests': [
    ],
}
