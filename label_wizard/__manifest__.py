{
    "name": "Labels wizard",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "category": "Custom",
    "summary": "Wizard for choosing how many labels to print",
    "depends": [
        "proxy_action",
        "product",
    ],
    "data": [
        "wizard/wizard_view.xml",
        "views/product.xml",
        "security/ir.model.access.csv",
    ],
}
