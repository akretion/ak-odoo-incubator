# -*- coding: utf-8 -*-
{
    'name': 'Product category available in pos by company',
    'version': '10.0.0.1.1',
    'category': 'Point Of Sale',
    'summary': "Set company_dependent to product.category.available_in_pos. Allows search from category",
    'author': 'Akretion',
    'website': 'https://akretion.com',
    "license": "AGPL-3",
    'depends': ['product', 'pos_remove_pos_category'],
    'data': ['views/product_category.xml'],
    'installable': True,
    'auto_install': False,
}
