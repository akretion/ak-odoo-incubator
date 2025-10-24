# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Auth Oauth Redirect Fix",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Fix OAuth login redirection",
    "category": "Tools",
    "depends": ["auth_oauth"],
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "data": [],
    "assets": {
        "web.assets_frontend": [
            "auth_oauth_redirect_fix/static/src/js/auth_oauth_redirect_fix.js",
        ],
    },
    "maintainers": ["paradoxxxzero"],
    "demo": [],
    "installable": True,
    "license": "AGPL-3",
}
