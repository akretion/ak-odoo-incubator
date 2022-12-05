{
    "name": "Base Customer Export",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "category": "Tools",
    "depends": ["base_export_manager"],
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "data": [
        "security/ir.model.access.csv",
        "views/ir_exports_config.xml",
        "views/ir_exports_line.xml",
    ],
    "maintainer": "florian-dacosta",
    "license": "AGPL-3",
    "installable": True,
}
