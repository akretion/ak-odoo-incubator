# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kalong",
    "version": "18.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Integrate Kalong debugger in Odoo",
    "category": "Tools",
    "depends": [],
    "external_dependencies": {
        "python": ["kalong", "websocket-client"],
    },
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "data": [
        "security/res_groups.xml",
        "security/ir_model_access.xml",
        "views/kalong_views.xml",
    ],
    "maintainers": ["paradoxxxzero"],
    "installable": True,
    "license": "AGPL-3",
}
