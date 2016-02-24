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


class StockWarehouseOrderpoint(Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_draft_procurements(self, cr, uid, ids, field_name, arg,
                                context=None):
        if context is None:
            context = {}
        result = {}
        procurement_obj = self.pool['procurement.order']
        for orderpoint in self.browse(cr, uid, ids, context=context):
            if orderpoint.location_destination_id:
                location_id = orderpoint.location_destination_id.id
            else:
                location_id = orderpoint.location_id.id
            procurement_ids = procurement_obj.search(
                cr, uid ,
                [('state', '=', 'draft'),
                 ('product_id', '=', orderpoint.product_id.id),
                 ('location_id', '=', location_id)])
            result[orderpoint.id] = procurement_ids
        return result


    _columns = {
        'location_destination_id': fields.many2one(
            'stock.location', 'Destination Location'),
        'procurement_draft_ids': fields.function(
            _get_draft_procurements, type='many2many',
            relation="procurement.order",
            string="Related Procurement Orders",
            help="Draft procurement of the product and location of that orderpoint"),
    }

