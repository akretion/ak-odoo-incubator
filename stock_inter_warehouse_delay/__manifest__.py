# -*- coding: utf-8 -*-
# Copyright 2019 Raphael Reverdy (Akretion)
{
    "name": "Stock Inter Warehouse delay",
    "version": "10.0.1.0.1",
    "category": "Stock",
    "summary": """When a warehouse ressuply
    another one, it's the delay between Picking OUT
    and Picking IN.
    """,
    "author": "Akretion",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/inter_wh.xml",
    ],
    "depends": [
        "stock",
    ],
    "installable": True,
}
