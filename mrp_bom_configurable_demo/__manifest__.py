{
    "name": "MRP Bom Configurable demo",
    "summary": "Skip components lines in bom according to conditions",
    "version": "16.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/manufacture",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp_bom_configurable", "sale_mrp_bom_configurable"],
    "maintainer": [
        "bealdav",
    ],
    "data": [
        "data/mrp_bom_configurable.xml",
        "views/demo_input_views.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
    "installable": True,
}
