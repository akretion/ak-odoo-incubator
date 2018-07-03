{
    'name': 'Stock Picklist',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'depends': [
        'stock_picking_wave',
    ],
    'description': """
Stock Picklist
==============

Adds a `Picklist` button to picking waves that provides a summary grouped by location 
and product for all of the pickings in the wave.
    """,
    'author': 'Hibou Corp., Akretion',
    'license': 'AGPL-3',
    'website': 'https://hibou.io/',
    'data': [
        'report/stock_wave_picklist.xml',
        'views/stock_views.xml',
    ],
    'installable': True,
    'application': False,
}
