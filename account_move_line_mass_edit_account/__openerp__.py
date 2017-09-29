# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account move line mass edit account",
    "summary": "Give the possibility to edit in mass the account on move line",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    'installable': False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "account",
    ],
    "data": [
        "wizards/mass_edit_move_line_account_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
