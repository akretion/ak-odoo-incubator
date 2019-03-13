# -*- coding: utf-8 -*-

{
    'name': 'Mrp Production Mark as Done',
    'summary': "Allows to set as 'Done' several manufacturing orders at once",
    'version': '10.0.1.0.0',
    'category': 'Manufacturing',
    'website': 'www.akretion.com',
    'author': 'Akretion,',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'mrp',
    ],
    'data': [
        'wizard/mrp_production_mark_done.xml',
    ],
}
