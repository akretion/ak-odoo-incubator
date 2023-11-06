# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Auth Oidc Environment",
    "summary": """
        This module allows to add auth oidc data for akretion""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-auth",
    "depends": [
        "auth_oidc",
    ],
    "data": ["data/ir_config_parameter_data.xml"],
    "demo": [],
}
