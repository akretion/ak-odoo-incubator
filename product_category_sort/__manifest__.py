# -*- coding: utf-8 -*-
# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Category Sort",
    "summary": "Give the posibility to sort the category",
    "version": "10.0.1.0.0",
    "category": "Product",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    # We should only depend on 'product'... but the product category
    # menu entry is located in the 'sale' module, so we depend on 'sale' :-(
    "depends": ["sale"],
    "data": [
        "views/product_category_view.xml",
    ],
    "installable": True,
}
