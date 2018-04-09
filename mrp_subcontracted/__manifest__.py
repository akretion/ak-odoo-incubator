# -*- coding: utf-8 -*-
{
    "name": "Subcontract manufacture",
    "summary": "Subcontract manufacturing orders",
    "version": "10.0.1.0.0",
    'category': 'Manufacturing',
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
        "subcontracted_service",
    ],
    "data": [
        "views/mrp.xml",
    ],
    "demo": [
        "demo/products.xml",
        "demo/mrp.xml",
    ],
}
