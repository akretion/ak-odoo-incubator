# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Product Pricelist Supplier Info",
    "summary": "Show supplier info on pricelist item",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "purchase",
        "sale",
        "product_supplierinfo_per_attribute_value",
        "product_pricelist_per_attribute_value",
    ],
    "data": ["views/product_pricelist_item_view.xml"],
    "demo": [],
}
