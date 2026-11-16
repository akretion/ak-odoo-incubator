# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Partner Credit Rating",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Provider agnostic credit rating on companies (base module)",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": ["base_setup", "contacts", "mail"],
    "data": [
        "security/ir.access.csv",
        "data/ir_cron.xml",
        "views/credit_rating.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
        "wizards/search.xml",
    ],
    "installable": True,
}
