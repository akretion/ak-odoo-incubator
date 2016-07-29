# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    Stock Delivery Prepare module for OpenERP                                 #
#    Copyright (C) 2014 Akretion Chafique Delli <chafique.delli@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

import netsvc
import base64
from openerp.osv import orm, fields
from openerp.tools.translate import _


class stock_picking_preparation(orm.TransientModel):
    _name = 'stock.picking.preparation'

    _columns = {
        'file': fields.binary('Delivery Orders File', readonly=True),
        'filename': fields.char('File Name'),
        'force_availability': fields.boolean('Force Availability'),
    }

    _defaults = {
        'filename': 'stock_picking_preparation.pdf',
        'force_availability': False,
    }

    def _force_availability(self, cr, uid, wiz, context):
        picking_obj = self.pool.get('stock.picking.out')
        if wiz.force_availability:
            assignable_picking_ids = picking_obj.search(cr, uid, [
                    ('id', 'in', context['active_ids']),
                    ('state', 'in', ['draft', 'confirmed']),
                ], context=context)
            if assignable_picking_ids:
                picking_obj.force_assign(
                    cr, uid, assignable_picking_ids, context)
        return True

    def start_preparation(self, cr, uid, ids, context):
        picking_obj = self.pool.get('stock.picking.out')
        for wiz in self.browse(cr, uid, ids, context=context):
            self._force_availability(cr, uid, wiz, context)
            unassigned_picking_ids = picking_obj.search(cr, uid, [
                    ('id', 'in', context['active_ids']),
                    ('state', 'not in', ['assigned']),
                ], context=context)
            if unassigned_picking_ids:
                picking_list = []
                for picking in picking_obj.browse(
                        cr, uid, unassigned_picking_ids, context=context):
                    picking_list.append(picking.name)
                raise orm.except_orm(
                    _('Error !'),
                    _("The delivery orders %s are not in 'Ready to Deliver "
                      "(assigned)' state") % picking_list)
            picking_obj.start(cr, uid, context['active_ids'], context=context)
            service = netsvc.LocalService('report.webkit.delivery_order')
            (result, format) = service.create(
                cr, uid,
                context['active_ids'], {'model': 'stock.picking.out'},
                context=context)
            self.write(cr, uid, ids, {'file': base64.b64encode(result)},
                       context=context)
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking.preparation',
                'res_id': ids[0],
                'target': 'new'}
