# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Tracking Sale Reconfirmation",
    "summary": "Tracking Sale Reconfirmation",
    "version": "16.0.1.0.0",
    "category": "sale",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "tracking_manager",
        "sale",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "views/sale_cancel_tracking.xml",
    ],
}
