# coding: utf-8
# © 2016 David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Completely Available Picking',
    'summary': "Display in a separate menu pickings out 'Ready to transfert'",
    'version': '8.0.0.0.1',
    'category': 'stock',
    'author': 'Akretion',
    'description': """
- Record date when picking became 'Ready to transfert'.
- Display in a separate menu 'Ready to transfert' pickings out
  and their available date
- Allow to order by picking list by this available date.

Author: David BEAL <david.beal@akretion.com>
""",
    'depends': [
        'stock',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'stock_view.xml',
    ],
    'installable': False,
    'license': 'AGPL-3',
}
