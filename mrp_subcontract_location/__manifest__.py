# coding: utf-8
{
    'name': 'MRP Subcontract Location',
    'version': '10.0.0.0.1',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'description': """
        Manage stock by location for subcontract manufacture order
 """,
    'depends': [
        'mrp_subcontracted',
    ],
    'data': [
        'data/data.xml',
        'views/res_partner.xml',
        'views/purchase.order.xml',
    ],
    'installable': True,
    'application': False,
}
