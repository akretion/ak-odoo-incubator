# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Journal Sale Refund Link",
    "summary": "Link Sale journal and Refund journal in order to set "
               "the right default value when doing a refund",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "account",
    ],
    "data": [
        "views/account_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
