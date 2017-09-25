# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "sale_discount_code",
    "summary": "Module to manage discount code",
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
        "sale",
    ],
    "data": [
        'views/sale_order.xml',
        'views/discount_code_rule.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
