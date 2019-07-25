# coding: utf-8
{
    'name': 'Purchase task',
    'version': '10.0.0.0.2',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'description': """
    Manage PO with tasks.
    """,
    'depends': [
        'purchase',
        'mrp_subcontract_location',
#        'purchase_order_buyer', # TODO être plus generique
    ],
    'data': [
        'data/purchase_project.xml',
        'views/purchase_order.xml',
        'views/project_task.xml',
    ],
    'installable': True,
    'application': False,
}
