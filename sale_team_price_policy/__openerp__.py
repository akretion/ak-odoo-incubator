# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Chafique DELLI <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Team Price Policy',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Akretion',
    'category': 'Sales',
    'summary': 'Add price policy management on sales and invoices',
    'depends': [
        'account_invoice_pricelist',
        'sales_team',
        'sale_order_price_recalculation',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/sale_team_view.xml',
        'views/sale_order_view.xml',
        'views/product_pricelist_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
