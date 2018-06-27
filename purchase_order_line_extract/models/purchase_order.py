# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    open_order = fields.Boolean(
        help="This kind of order can't be tranfered. The lines and "
             "quantity can be extract to a normal PO")

    @api.multi
    def open_extract_line_items(self):
        """
            Open purchase order lines of selected purchase orders
            It is used to update purchase order line date planned
            after order validation.
        """
        extract_line_ids = []
        extract_line_obj = self.env['purchase.order.extract.line']
        for po in self:
            if not po.open_order:
                raise exceptions.Warning(
                    _('Order %s is not an open order, it is not possible '
                      'to extract lines from it to a new order.' % po.name))
            for line in po.order_line:
                if line.state == 'cancel':
                    continue
                vals = {
                    'purchase_line_id': line.id,
                    'extract_quantity': line.product_qty,
                }
                extract_line = extract_line_obj.create(vals)
                extract_line_ids.append(extract_line.id)
        action = self.env.ref(
            'purchase_order_line_extract.purchase_order_extract_line_action')
        result = action.read()[0]
        result['domain'] = (
            "[('id','in',[" + ','.join(map(str, extract_line_ids)) + "])]"
        )
        return result

    @api.multi
    def write(self, vals):
        if vals.get('open_order', False):
            for po in self:
                pickings = po.picking_ids
                if any([p.state  in ('cancel', 'done') for p in pickings]):
                    raise exceptions.Warning(
                        _('Impossible to change order %s to an open order '
                          'because some actions have already been made on '
                          'linked incoming shipments' % po.name))
        return super(PurchaseOrder, self).write(vals)
