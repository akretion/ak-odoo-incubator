# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Claim Simple Repair',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """Really simple module to manage your repairs
    by creating a new repair picking from the sale order""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'sale_stock',
        ],
    'data': [
        'wizards/generate_picking_repair_view.xml',
        'views/sale_view.xml',
        'views/product_view.xml',
        'data/product_data.xml',
        ],
    'demo': [],
    'installable': True,
}
