# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Partner Credit Rating Creditsafe",
    "version": "20.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Creditsafe scores as credit rating provider",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": ["partner_credit_rating"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "views/credit_rating.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
}
