# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Rental Duration",
    "summary": "SUMMARY",
    "version": "16.0.1.0.0",
    "category": "rental",
    "website": "https://github.com/OCA/vertical-rental",
    "author": "Akretion, Odoo Community Association (OCA), , Groupe Voltaire SAS",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "rental_variant",
    ],
    "data": [
        "data/data.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
        "views/sale_rental.xml",
        "views/res_config_settings.xml",
        "wizards/sale_rental_wizard.xml",
    ],
}
    
