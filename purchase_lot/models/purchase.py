# -*- coding: utf-8 -*-
# © 2017 David BEAL <david.beal@akretion.com>, Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Serial Number',
        readonly=True)

    @api.multi
    def _create_stock_moves(self, picking):
        moves = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for move in moves:
            if move.purchase_line_id.lot_id:
                move.write(
                    {'restrict_lot_id': move.purchase_line_id.lot_id.id})
        return moves


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        res = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier)
        if self.product_id.auto_generate_prodlot:
            res['lot_id'] = self.lot_id.id
        return res

    # Need to merge https://github.com/akretion/odoo/tree/9.0-hooks
    @api.model
    def check_merge_po_line(self, line, procurement):
        res = super(ProcurementOrder, self).check_merge_po_line(
            line, procurement)
        if not line.lot_id == procurement.lot_id:
            return False
        else:
            return res
