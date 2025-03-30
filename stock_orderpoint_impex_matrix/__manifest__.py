# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Orderpoint Import Export Per Warehouse",
    "summary": """
        Import and export orderpoints according to chosen warehouses""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://www.akretion.com",
    "depends": ["stock"],
    "data": [
        "wizard/wizard_orderpoint_matrix_export.xml",
        "wizard/wizard_orderpoint_matrix_import.xml",
    ],
    "demo": ["demo/demo.xml"],
    "external_dependencies": {"python": ["openpyxl"]},
}
