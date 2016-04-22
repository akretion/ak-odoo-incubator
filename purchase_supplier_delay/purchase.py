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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(BaseModel):
    _inherit = 'purchase.order'

    def action_picking_create(self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            partner = po.partner_id
            if po.picking_ids:
                continue
            for po_line in po.order_line:
                if not po_line.product_id:
                    continue
                product = po_line.product_id
                delay = 0
                for supplier in product.seller_ids:
                    if partner and (supplier.name.id == partner.id):
                        supplierinfo = supplier
                        delay = supplier.delay
                        break
                delay = int(delay) or partner.delivery_delay or 0
                today = datetime.today().date()
                date_planned = today + relativedelta(days=delay)
                vals = {
                    'date_planned': date_planned.strftime(
                            DEFAULT_SERVER_DATE_FORMAT)
                }
                po_line.write(vals)
        return super(PurchaseOrder, self).action_picking_create(
                cr, uid, ids, context=context)
