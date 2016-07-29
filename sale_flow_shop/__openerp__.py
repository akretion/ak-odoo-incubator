# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Chafique Delli
#    Copyright 2014 Akretion SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Sale Flow Shop',
    'version': '1.0.0',
    'category': 'Generic Modules',
    "author" : "Akretion",
    'license': 'AGPL-3',
    'description': """
""",
    "website" : 'http://wwww.akretion.com/',
    'depends': ['sale_stock',
                'account',
                'sale_journal_shop',
                'account_journal_sale_refund_link',
                ],
    'data': ['sale_view.xml',
             'account_invoice_view.xml',
             'stock_view.xml',
             ],
    'installable': True,
    'auto_install': False,
}
