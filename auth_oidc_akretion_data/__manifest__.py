# Copyright 2023 AKretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Auth Oidc akretion configuration data",
    "summary": """
        This module add auth oidc configuration data for akretion""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": [
        "auth_oidc",
    ],
    "data": ["data/ir_auth_oauth_provide_data.xml"],
    "demo": [],
}
