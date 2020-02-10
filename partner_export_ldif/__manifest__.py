# -*- coding: utf-8 -*-
{
    "name": "Partner Export .ldif",
    "summary": "Export partner modifications as .ldif file",
    "version": " 10.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": ["ldap"],
    },
    "depends": [
        "base",
    ],
    "data": [
        "wizard/partner_generate_ldif_wizard.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
