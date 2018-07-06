# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class PurchaseOrderExtractLine(models.TransientModel):
    _name = 'purchase.order.extract.line'

    purchase_line_id = fields.Many2one(
        'purchase.order.line', string='Purchase Line', required=True)
    purchase_id = fields.Many2one(
        related='purchase_line_id.order_id',
        store=True,
        readonly=True)
    product_id = fields.Many2one(
        related='purchase_line_id.product_id',
        store=True,
        readonly=True)
    date_planned = fields.Date(
        related='purchase_line_id.date_planned',
        store=True,
        readonly=True)
    quantity = fields.Float(
        related='purchase_line_id.product_qty',
        store=True,
        readonly=True)
    product_uom = fields.Many2one(
        related='purchase_line_id.product_uom',
        store=True,
        readonly=True)
    partner_id = fields.Many2one(
        related='purchase_line_id.order_id.partner_id',
        store=True,
        readonly=True)
    extract_quantity = fields.Float(default=0.0)
    extractor_wizard_id = fields.Many2one('purchase.line.extractor.wizard')

    @api.multi
    def generate_new_po_line(self, po, expected_date):
        self.ensure_one()
        copy_vals = {
            'order_id': po.id,
            'product_qty': self.extract_quantity,
            'date_planned': expected_date,
            'origin_order_id': self.purchase_id.id,
        }
        self.purchase_line_id.copy(copy_vals)

    @api.multi
    def update_quantity_extracted(self, move):
        self.ensure_one()
        po_line = self.purchase_line_id
        if self.extract_quantity >= self.quantity:
            move.action_cancel()
            po_line.write({'product_qty': 0.0})
        else:
            move_obj = self.env['stock.move']
            new_move_id = move_obj.split(move, self.extract_quantity)
            new_move = move_obj.browse(new_move_id)
            new_move.action_cancel()
            vals = {
                'product_qty': self.quantity - self.extract_quantity,
            }
            po_line.write(vals)
