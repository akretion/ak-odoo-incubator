# Copyright 2024 David BEAL @ akretion
{
    "name": "Account Stock Situation",
    "version": "16.0.1.0.0",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": [
        "account",
        "stock",
    ],
    "data": [
        "views/config_settings.xml",
        "views/action.xml",
    ],
    "external_dependencies": {"python": ["polars"]},
    "installable": True,
}
