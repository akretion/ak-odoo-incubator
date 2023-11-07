# Copyright 2023 AKretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Auth Oidc akretion data",
    "summary": """
        This module allows to add auth oidc data for akretion""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-auth",
    "depends": [
        "auth_oidc",
    ],
    "data": ["data/ir_auth_oauth_provide_data.xml"],
    "demo": [],
}
