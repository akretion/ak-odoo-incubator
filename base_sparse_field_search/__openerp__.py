# -*- coding: utf-8 -*-
{
    "name": "Sparse Fields Search",
    "summary": "Search feature for sparse field",
    "version": "9.0.1.0.0",
    'category': 'Technical Settings',
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
        "base_sparse_field",
    ],
    "data": [
        'views/ir_model_fields.xml',
    ]
}
