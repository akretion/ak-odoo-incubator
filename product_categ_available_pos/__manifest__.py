# -*- coding: utf-8 -*-
{
    'name': 'Product category available in pos by company',
    'version': '10.0.0.1.1',
    'category': 'Point Of Sale',
    'description': """
Set company_dependent to product.category.available_in_pos.
Use a method to set it properly on ancestors.
Change search and search_read in order to search from category.
    """,
    'author': 'Akretion',
    'website': 'https://akretion.com',
    'depends': ['product', 'pos_remove_pos_category'],
    'data': ['views/product_category.xml'],
    'installable': True,
    'auto_install': False,
}
