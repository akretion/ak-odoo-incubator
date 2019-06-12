# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    qty_received = fields.Float(compute='_compute_qty_received2')

    @api.depends('order_id.state', 'move_ids.state')
    def _compute_qty_received2(self):
        """Manage quantity of services products.

        The goal is to allow invoicing of done quantities.

        The move is linked to the the line.
        Ensure we are looking a move about the finished product
        and not the raw materials.
        """
        # todo tester l'heritage :
        # if not ours: self._compute_quantity_received() ?
        # ou alors super ?
        for line in self:
            if line.order_id.state not in ['purchase', 'done']:
                line.qty_received = 0.0
                continue
            if (
                line.product_id.type not in ['consu', 'product'] and
                not line.move_ids
            ):
                line.qty_received = line.product_qty
                continue

            total = 0.0
            if line._is_service_procurement():
                mo = line.mo_id
                if mo.state == 'done':
                    for move in mo.move_finished_ids:
                        if move.product_uom != line.product_uom:
                            total += move.product_uom._compute_quantity(
                                move.product_uom_qty, line.product_uom)
                        else:
                            total += move.product_uom_qty
            else:
                for move in line.move_ids:
                    if move.state == 'done':
                        if move.product_uom != line.product_uom:
                            total += move.product_uom._compute_quantity(
                                move.product_uom_qty, line.product_uom)
                        else:
                            total += move.product_uom_qty
            line.qty_received = total
