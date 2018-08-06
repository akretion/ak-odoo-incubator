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
        if not supplier.location_id:
            raise exceptions.ValidationError(
                _('No location configured on the subcontractor'))
        self.location_src_id = supplier.location_id.id
        self.location_dest_id = supplier.location_id.id
        wh = supplier.location_id.get_warehouse()
        self.picking_type_id = wh.manu_type_id.id
        self.move_raw_ids.write({
            'warehouse_id': wh.id,
            'location_id': supplier.location_id.id,
        })
        self.move_finished_ids.write({
            'warehouse_id': wh.id,
            'location_dest_id': supplier.location_id.id,
        })

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

        moves_in = self.env['stock.move']
        proc_obj = self.env['procurement.order']
        inter_location_id = self.env.ref(
             'stock.stock_location_inter_wh'
         ).id
        supplier_wh = supplier.location_id.get_warehouse()
        old_pickings = self.env['stock.picking']
        for raw_move in self.move_raw_ids:
            # If there is a purchase order or request, not validated yet
            # It seems complicated to change it manually, since it could be
            # together with other product which do not need to change location...
            # For now, the user should do it manually.
            # TODO
            # Maybe we could display a wizard witl all impacted POs before validation
            move_in = raw_move.move_orig_ids
            moves_in |= move_in
            if not update:
                continue
            if not move_in:
#                proc = proc_obj.search([
#                    ('move_dest_id', '=', raw_move.id),
#                    ('state', 'in', ('exception', 'confirmed', 'running')),
#                    '|', ('purchase_line_id', '!=', False),
#                    ('request_id', '!=', False)])
#                if not proc:
   #                # make to stock, nothing to do
                continue
#                if proc.purchase_id:
                    # sortir ligne de PO de la PO et la mettre dans une nouvelle???
#                else proc.request_id:
                    # Changement sur la request... plusieurs PO en brouillon créées??
            else:
                if move_in.purchase_line_id:
                    # TODO si orig a un PO => PO en cours à changer...
                    pass
                else:
                    if move_in.location_id.id != inter_location_id:
                        _logger.info('probleme, devrait jamais arriver?')
                        continue
                    move_out = move_in.move_orig_ids
                    if not move_out:
                        _logger.info('pas de move_out, impossible?')
                    # We can't do anything it is is already sent
                    # #TODO Warn the user??
                    if move_in.state == 'done' or move_out.state == 'done':
                        continue
                    old_pickings |= move_in.picking_id
                    move_in.picking_id = False
                    move_in.location_dest_id = supplier.location_id.id
                    move_in.warehouse_id = supplier_wh.id
                    move_in.picking_type_id = supplier_wh.in_type_id.id
                    move_in.assign_picking()

                    old_pickings |= move_out.picking_id
                    move_out.picking_id = False
                    move_out.partner_id = supplier.id
                    move_out.assign_picking()
                    # assign_picking

            # TODO update procurements?
        for picking in old_pickings:
            if not picking.move_lines:
                picking.unlink()
        return moves_in

    @api.multi
    def update_moves_after_production(self, supplier, update=False):
        # Modify outgoing move and create a second one herebefore
        # It's easier to add new move before the existing one
        moves_out = self.env['stock.move']
        moves_out_dest = self.env['stock.move']
        supplier_wh = supplier.location_id.get_warehouse()
        old_pickings = self.env['stock.picking']
        for finish_move in self.move_finished_ids:
            if not finish_move.move_dest_id:
                _logger.info('impossible?')
                continue
            # TODO maybe need to handle last delivery move. (coming from SO)
            move_out = finish_move.move_dest_id
            move_out_dest = move_out.move_dest_id
            moves_out |= move_out
            moves_out_dest |= move_out_dest

            if not update:
                continue
            old_pickings |= move_out.picking_id
            # TODO update procurements?
            move_out.picking_id = False
            move_out.location_id = supplier.location_id.id
            move_out.warehouse_id = supplier_wh.id
            move_out.picking_type_id = supplier_wh.out_type_id.id
            move_out.assign_picking()

            if moves_out_dest:
                old_pickings |= move_out_dest.picking_id
                move_out_dest.picking_id = False
                move_out_dest.partner_id = supplier.id
                move_out_dest.assign_picking()
        for picking in old_pickings:
            if not picking.move_lines:
                picking.unlink()
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
