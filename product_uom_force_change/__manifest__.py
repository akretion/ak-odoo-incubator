# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Product UOM force change",
    "summary": "Allow to force a uom change an already used product",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Stock",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "stock",
    ],
    "data": [
        "wizards/product_change_uom_view.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
