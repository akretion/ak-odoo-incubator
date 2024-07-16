# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Pallet Filling",
    "summary": """
        Calculate pallet fillings from product volumes on pickings and sale orders""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": ["sale_stock"],
    "data": [
        "views/stock_package_type.xml",
        "views/stock_picking.xml",
        "views/sale_order.xml",
    ],
    "demo": [],
}
