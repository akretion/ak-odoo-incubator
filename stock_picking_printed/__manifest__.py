# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Printed",
    "summary": "Stock Picking Printed",
    "version": "8.0.1.0.0",
    "category": "Warehouse",
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
        "stock",
    ],
    "data": [
        "views/stock_picking_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
