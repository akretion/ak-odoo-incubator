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

from openerp.osv.orm import BaseModel, Model
from openerp.osv import fields
from datetime import datetime, timedelta


class ProductSupplierinfo(BaseModel):
    _inherit = 'product.supplierinfo'

    def _get_product_supplier_delay(
            self, cr, uid, ids, name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        product_obj = self.pool['product.product']
        for sup_info in self.browse(cr, uid, ids, context=context):
            partner_id = sup_info.name.id
            # In v8 we can remove this but there is perf problem in v7 with a
            # search when we propose it to OCA
            cr.execute("""
                SELECT p.id
                FROM product_product p
                WHERE p.product_tmpl_id = %s
            """, (sup_info.product_id.id,))
            product_ids = [x[0] for x in cr.fetchall()]
#            product_ids = product_obj.search(
#                    cr, uid, [('product_tmpl_id', '=', sup_info.product_id.id)])
            limit = sup_info.company_id.incoming_shippment_number_delay or 3
            cr.execute("""
                SELECT po.date_approve, pi.date_done
                FROM stock_move m
                    JOIN stock_picking pi ON pi.id = m.picking_id
                    JOIN purchase_order_line l ON l.id = m.purchase_line_id
                    JOIN purchase_order po ON po.id = l.order_id
                WHERE m.product_id in %s AND pi.type = 'in'
                    AND m.state = 'done'
                GROUP BY po.date_approve, pi.date_done
                ORDER BY pi.date_done desc
                LIMIT %s
            """, (tuple(product_ids), limit))
            dates = cr.fetchall()
            if not dates:
                continue
            delays = []
            for delay_info in dates:
                if not delay_info[0] or not delay_info[1]:
                    continue
                date_approve = datetime.strptime(
                        delay_info[0], '%Y-%m-%d').date()
                date_done = datetime.strptime(
                        delay_info[1], '%Y-%m-%d %H:%M:%S').date()
                delays.append((date_done - date_approve).days)
            if not delays:
                continue
            res[sup_info.id] = int(round(float(sum(delays))/len(delays)))
        return res

    _columns = {
        'delay': fields.function(
            _get_product_supplier_delay, type='integer',
            string='Delay')
    }
