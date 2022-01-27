# -*- coding: utf-8 -*-
# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Picking Type Restrict Location",
    "version": "8.0.1.0.0",
    "category": "Tools",
    "website": "https://akretion.com",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "summary": "Prevent some location src/dest couples for picking types",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_type_views.xml",
    ],
}
