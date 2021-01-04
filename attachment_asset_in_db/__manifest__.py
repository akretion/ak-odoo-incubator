# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "attachment_asset_in_db",
    "summary": "Always store odoo asset in database",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
    ],
    "data": [],
    "post_init_hook": "post_init_hook",
    "demo": [],
    "qweb": [],
}
