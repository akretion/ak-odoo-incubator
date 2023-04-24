{
    "name": "Warehouse Printing Server Configuration",
    "summary": "Allow to set printing configuration in warehouse areas",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/warehouse.xml",
        "views/company.xml",
        "views/print_config.xml",
        "security/ir.model.access.csv",
    ],
}
