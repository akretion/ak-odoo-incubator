# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Akretion (<http://www.akretion.com>).
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

from openerp.osv.orm import Model
from openerp.osv import fields, orm


class PurchaseEdiProfile(Model):
    _name = "purchase.edi.profile"
    _inherits = {'ir.exports': 'export_id'}


    def _get_edi_file_format(self, cr, uid, context=None):
        return [
            ('csv', 'CSV'),
            ('xls', 'Excel'),
        ]

    _columns = {
        'suppplier_info_ids': fields.one2many(
            'product.supplierinfo',
            'purchase_edi_id',
            'Suppliers Info'),
        'file_format': fields.selection(
            _get_edi_file_format,
            required=True,
            string='File Format'),
        'export_id': fields.many2one(
            'ir.exports',
            'Export',
            required=True,
            ondelete='restrict',
            domain=[('resource', '=', 'purchase.order.line')]),
    }

