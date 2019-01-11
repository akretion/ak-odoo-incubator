# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Mail Via",
    "summary":
        "Change the from email with a via email when sending back email",
    "version": "10.0.1.0.0",
    "category": "Mail",
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
        "mail",
    ],
    "data": [
        "data/mail_data.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
