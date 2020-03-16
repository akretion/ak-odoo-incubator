# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Simple Valuation",
    "summary": "Valuation of inventories according to custom rules",
    "description": """
        Display cost information from different sources in inventory line""",
    "author": "Akretion",
    "website": "http://www.akretion.com",
    "category": "Stock",
    "version": "12.0.1.0.0",
    "depends": ["stock", "account", "purchase", "report_xlsx"],
    "data": ["views/inventory_view.xml", "report/report_view.xml"],
    "maintainers": ["bealdav", "PierrickBrun", "mourad-ehm", "kevinkhao"],
}
