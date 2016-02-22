# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Stock Picking Refund Backorder',
 'version': '0.0.1',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'description': """This module give the posibility to cancel and refund
 the backorder in one click
 """,
 'depends': [
     'stock',
 ],
 'data': [
     'wizards/stock_picking_refund_backorder_view.xml',
     'views/stock_picking_view.xml',
 ],
 'installable': True,
 'application': True,
}
