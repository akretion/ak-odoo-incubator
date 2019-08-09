# coding: utf-8
{
    'name': 'Order Point Traffic lights',
    'version': '10.0.0.0.1',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Stock',
    'description': """
        Show Green / Orange / Red flights on ordre points.

    Green : no need to order
    Orange : need to order now
    Red: Too late
    Greatly inspired from (Eficent / OCA) DDRMP
 """,
    'depends': [
        "purchase",
        "mrp_bom_location",
        "web_tree_dynamic_colored_field",
        "stock_warehouse_orderpoint_stock_info",
        "stock_warehouse_orderpoint_stock_info_unreserved",
        "stock_available_unreserved",
        "stock_orderpoint_uom",
        "stock_orderpoint_manual_procurement",
    #    "mrp_mto_with_stock",
        "base_cron_exclusion",
        "stock_orderpoint_purchase_link",  # v11
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        "views/stock_warehouse_orderpoint_view.xml",
        "views/procurement_order_view.xml",
        "views/mrp_production_view.xml",
        "views/purchase_order_line_view.xml",
        "views/mrp_bom_view.xml",
        'views/product.xml',
        "views/make_procurement_views.xml",
    ],
    'installable': True,
    'application': False,
}
