# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Delivery Promotion Rule",
    "summary": "Module to manage promotion rule on sale order with delivery",
    "version": "8.0.1.0.0",
    "category": "Sale",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_promotion_rule",
        "delivery"
    ],
    "data": [
        "views/sale_promotion_rule_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
