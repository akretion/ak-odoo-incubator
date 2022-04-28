# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Akretion (<http://www.akretion.com>).
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

{'name': 'Base EDI',
 'version': '0.1',
 'author': 'Akretion,Odoo Community Association (OCA)',
 'website': 'http://www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules/Others',
 'summary': 'Export',
 'depends': ['base_export_reorder',
             'external_file_location',
             ],
 'data': [
      'ir_exports_view.xml',
 ],
 'installable': True,
 }
