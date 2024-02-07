# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Script File Import",
    "summary": "base module for import with script",
    "version": "14.0.1.0.0",
    "category": "tools",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pattern_import_export",
    ],
    "data": [
        "views/menu.xml",
        "views/script_file_import.xml",
        "security/ir.model.access.csv",
    ],
}
