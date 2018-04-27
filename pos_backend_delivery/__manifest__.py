# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pos backend delivery",
    "summary": "Display transfert in the back in a simple way",
    "version": "10.0.1.0.0",
    "category": "Uncategorized",
    "website": "www.akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "stock",
        "pos_backend_communication",
    ],
    "data": [
        'views/stock_picking.xml',
        'views/assets.xml',
    ],
    "qweb": [
    ]
}
