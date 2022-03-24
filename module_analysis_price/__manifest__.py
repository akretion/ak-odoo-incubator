# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Module Analysis Price",
    "summary": "Module Analysis Price",
    "version": "14.0.1.0.0",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "module_analysis",
    ],
    "data": [
        "views/assets.xml",
        "views/ir_module_type_view.xml",
        "views/ir_module_author_view.xml",
        "views/ir_module_type_rule_view.xml",
        "views/ir_module_module_view.xml",
        "data/module_type_data.xml",
        "data/module_type_rule_data.xml",
    ],
    "qweb": [
        "static/src/xml/module_dashboard.xml",
    ],
    "demo": [],
}
