# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def update_warehouse(self, wh, move_type):
        self.ensure_one()
        if move_type == 'out':
            vals = {
                'picking_type_id': wh.out_type_id.id,
                'location_id': wh.lot_stock_id.id,
                'warehouse_id': wh.id,
                'picking_id': False,
            }
        else:
            # TODO if needed...
            picking_type_id = wh.in_type_id.id
        picking = self.picking_id
        self.write(vals)
        if picking and not picking.move_lines:
            picking.unlink()
        
