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


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def update_locations(self, supplier):
        self.ensure_one()
        if not supplier.reception_location_id:
            raise exceptions.ValidationError(
                _('No location configured on the subcontractor'))
        self.location_src_id = supplier.reception_location_id.id
        self.location_dest_id = supplier.manufacture_location_id.id
        self.picking_type_id = supplier.manufacture_location_id.get_warehouse().manu_type_id

    @api.multi
    def update_moves_before_production(self, supplier, update=False):
        """Change products locations according to mo's location

        Workflow
        1) a subcontracted MO in WH/Stock is created due to some procurments
        2) when a subcontracted service is bought to a supplier it changes
        the mo's locations (where raw materials are taken and produced product is put):
        (it changes from WH/Stock to A_SUPPLIER/Stock)
        3) related moves should be then changed: instead of taken goods from WH/STOCK 
        it shoud take them from A_SUPPLIER/Stock.
        WH/Stock > Virt/Production becomes
        WH/Stock > A_SUPPLIER/Stock + A_SUPPLIER/Stock > Virt/Production
        4) pickings should then be added :
        WH/Stock > A_SUPPLIER/Stock is changed to
        Virt/Inter-warehouse > A_SUPPLIER/Stock and it's added to a
        new picking A_SUPPLIER:Receipts
        Add moves between Stock and Production."""
        self.ensure_one()

        # Modify incoming move and create a second one hereafter
        # It's easier to add new moves after existing ones.
        moves_in = self.env['stock.move']
        for move_in in self.move_raw_ids:
            if not move_in.move_orig_ids:
                # TODO should be done in upadte_mo()
                move_in.location_id = supplier.reception_location_id.id
                move_in.warehouse_id = supplier.reception_location_id.get_warehouse().id
                continue
            if not update:
                moves_in |= move_in.move_orig_ids
                continue
            # TODO Would be better to not create it at the first place
            # TODO should be done in upadte_mo()
            move_in.location_id = supplier.reception_location_id.id
            move_in.warehouse_id = supplier.reception_location_id.get_warehouse().id
#            move_in.picking_type_id = supplier.reception_location_id.get_warehouse().manu_type_id.id
            move_in.move_orig_ids.location_dest_id = supplier.reception_location_id.id
            move_in.move_orig_ids.picking_type_id = supplier.reception_location_id.get_warehouse().in_type_id.id
            move_in.move_orig_ids.warehouse_id = supplier.reception_location_id.get_warehouse().id
            moves_in |= move_in.move_orig_ids
            # TODO update procurements?
        return moves_in

    @api.multi
    def update_moves_after_production(self, supplier, update=False):
        # Modify outgoing move and create a second one herebefore
        # It's easier to add new move before the existing one
        moves_out = self.env['stock.move']
        moves_out_dest = self.env['stock.move']
        for move_out in self.move_finished_ids:
            if not move_out.move_dest_id:
                continue
            # TODO maybe need to handle last delivery move. (coming from SO)
            if not update:
                move_out.move_dest_id.picking_type_id = supplier.manufacture_location_id.get_warehouse().out_type_id.id
                moves_out |= move_out.move_dest_id
                moves_out_dest |= move_out.move_dest_id.move_dest_id
                continue
            # TODO update procurements?
            # TODO should be done in upadte_mo()
            move_out.location_dest_id = supplier.manufacture_location_id.id
            move_out.warehouse_id = supplier.manufacture_location_id.get_warehouse().id
            move_out.move_dest_id.location_id = supplier.manufacture_location_id.id
            move_out.move_dest_id.warehouse_id = supplier.manufacture_location_id.get_warehouse().id
            move_out.move_dest_id.picking_type_id = supplier.manufacture_location_id.get_warehouse().out_type_id.id
            moves_out |= move_out.move_dest_id
            moves_out_dest |= move_out.move_dest_id.move_dest_id
        return moves_out, moves_out_dest

    @api.multi
    def write(self, vals):
        """Propagate date_planned start to previous move."""

        # lorsqu'on change la date de la mo
        #  on change la date de reception associée
        # est-ce vraiment utile ??
        res = super(MrpProduction, self).write(vals)
        if 'date_planned_start' in vals:
            inter_wh = self.env.ref('stock.stock_location_inter_wh')

            for move_in in self.move_raw_ids.filtered(
                lambda r: r.state not in ['done', 'cancel']
            ):
                for previous_move in move_in.move_orig_ids:
                    if previous_move.location_id != inter_wh:
                        _logger.warning('precedent non concernee')
                        continue
                    if len(move_in.move_orig_ids) > 1:
                        _logger.warning('devrait pas arriver !')
                    previous_move.date_expected = move_in.date_expected
                    _logger.info('date du precedent pickng changee')
            _logger.info('pour le moment on fait pas les move out')
        return res
