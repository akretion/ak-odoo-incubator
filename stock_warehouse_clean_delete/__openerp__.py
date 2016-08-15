# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Clean Warehouse delete",
    'description': """
Remote records related to a warehouse when you delete it
(routes, sequences etc...)""",
    'author': "Akretion",
    'website': "http://www.akretion.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'stock',
    ],
    'installable': False,
}
