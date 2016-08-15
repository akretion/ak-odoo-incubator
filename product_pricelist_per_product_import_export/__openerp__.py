# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Supplier Import/Export",
    "summary": "Add computed field to import and export"
               "easilier the product suuplier info",
    "version": "8.0.1.0.0",
    "category": "Product",
    "website": "https://odoo-community.org/",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "product_supplierinfo_variant",
        "pricelist_per_product",
        "product_variant_import_export",
    ],
    "data": [
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
