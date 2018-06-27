# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################

{
    'name': 'Purchase Order Line Extract',
    'version': '8.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'purchase'
        ],
    'data': [
        'views/purchase_order_view.xml',
        'views/purchase_order_extract_line.xml',
        'wizard/purchase_line_extractor_wizard.xml',
        ],
    'installable': True,
}

