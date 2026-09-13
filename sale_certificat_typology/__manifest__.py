# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Certificat Typology",
    "version": "14.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "views/product.xml",
        "views/certificat_typology.xml",
        "data/ir_cron_data.xml",
    ],
    "installable": True,
}
