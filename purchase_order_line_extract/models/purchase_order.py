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
        track_visibility='onchange',
        help="This kind of order can't be tranfered. The lines and "
             "quantity can be extract to a normal PO")

    @api.model
    def _get_picking_vals(self, order):
        vals = super(PurchaseOrder, self)._get_picking_vals(order)
        vals['open_order'] = order.open_order
        return vals

    @api.multi
    def open_extract_line_items(self):
        """
            Open purchase order lines of selected purchase orders
            It is used to update purchase order line date planned
            after order validation.
        """
        lines = []
        for po in self:
            if not po.open_order:
                raise exceptions.Warning(
                    _('The Order is not an open order, it is not possible '
                      'to extract lines from it to a new order.'))
            for line in po.order_line:
                if line.state == 'cancel' or not line.product_qty:
                    continue
                line_vals = {
                    'purchase_line_id': line.id,
                }
                lines.append((0, 0, line_vals))
        wizard_vals = {
            'origin': ', '.join(self.mapped('name')),
            'picking_type_id': self[0].picking_type_id.id,
            'expected_date': self[0].minimum_planned_date,
            'date_order': self[0].date_order,
            'line_ids': lines,
        }
        wiz = self.env['purchase.line.extractor.wizard'].create(wizard_vals)

        action = self.env.ref(
            'purchase_order_line_extract.purchase_line_extractor_action')
        result = action.read()[0]
        view = self.env.ref(
            'purchase_order_line_extract.purchase_line_extractor_wizard_form')
        result['res_id'] = wiz.id
        return result

    @api.multi
    def write(self, vals):
        if 'open_order' in vals:
            for po in self:
                pickings = po.picking_ids
                if any([p.state  in ('cancel', 'done') for p in pickings]):
                    raise exceptions.Warning(
                        _('Impossible to change the order to an open order '
                          'or to make it a classic order '
                          'because some actions have already been made on '
                          'linked incoming shipments'))
                pickings.write({'open_order': vals['open_order']})
        return super(PurchaseOrder, self).write(vals)
