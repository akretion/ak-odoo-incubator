# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Partner Credit Rating Allianz Trade",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Allianz Trade grades as credit rating provider",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": ["partner_credit_rating"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "views/res_config_settings.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
