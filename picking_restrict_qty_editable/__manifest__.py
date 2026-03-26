# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Picking Restrict Qty Editable",
    "summary": "Picking Restrict Qty Editable",
    "version": "14.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
}
