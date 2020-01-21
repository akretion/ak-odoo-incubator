# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# helper
#
# UPDATE account_move SET is_writeoff=True
# WHERE id IN (
# select move_id from account_move_line
# where name ilike 'Automatic Write Off'
#     or name ilike 'Write-off'
#     or name = 'Amortissement Automatique')

{
    "name": "Account Unreconcile Clean",
    "summary": "Clean write off when unreconcile",
    "version": "10.0.1.0.0",
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
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
