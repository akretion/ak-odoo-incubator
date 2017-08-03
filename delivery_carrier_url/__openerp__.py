# -*- coding: utf-8 -*-
#  Copyright (C) 2017 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Delivery Carrier Tracking URL",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "warehouse",
    "website": "https://www.akretion.com/",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base_delivery_carrier_label",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/delivery_view.xml",
        "views/stock_quant_package_view.xml",
    ],
}
