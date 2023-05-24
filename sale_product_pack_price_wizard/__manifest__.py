# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Product Pack Price Wizard",
    "description": """
        Adjust pack price from any of its line""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": [
        "sale_management",
        "sale_product_pack",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_line_pack_price.xml",
    ],
    "demo": [],
}
