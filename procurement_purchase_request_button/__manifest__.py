# coding: utf-8
{
    'name': 'Procurement Purchase Request Button ',
    'version': '10.0.1.0.0',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Purchase Management',
    'description': """
        Add a smart button linked to the purchase request
 """,
    'depends': [
        'purchase_request_procurement',
    ],
    'data': [
        'views/procurement_order.xml',
        'views/purchase_request.xml',
    ],
    'installable': True,
    'application': False,
}
