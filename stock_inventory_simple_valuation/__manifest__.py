# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Simple Valuation",
    "summary": "Get cost information from different sources in inventory",
    "author": "Akretion",
    "website": "http://www.akretion.com",
    "category": "Stock",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "depends": ["stock", "report_xlsx", "purchase"],
    "data": [
        "views/inventory_view.xml",
        "views/product_view.xml",
        "report/report_view.xml",
    ],
    "installable": True,
}
