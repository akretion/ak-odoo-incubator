# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Desktop Certificats",
    "summary": "Generate and manage TSL certificates of users",
    "version": "12.0.1.0.0",
    "category": "tools",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "mail",
    ],
    "data": [
        "data/data.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/rule.xml",
        "views/desktop.xml",
        "views/desktop_certificate.xml",
    ],
}
