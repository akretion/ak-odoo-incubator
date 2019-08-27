# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def update_locations(self, supplier_wh, supplier_loc):
        self.ensure_one()
        if not supplier_loc:
            raise exceptions.ValidationError(
                _('No location configured on the subcontractor'))
        self.location_src_id = supplier_loc.id
        self.location_dest_id = supplier_loc.id
        self.picking_type_id = supplier_wh.manu_type_id.id
        self.move_finished_ids.write({
            'warehouse_id': supplier_wh.id,
            'location_dest_id': supplier_loc.id,
        })

    @api.multi
    def cancel_row_move_ids(self, cancel_linked_proc=True):
        """Cancel raw move ids.

        If cancel_linked_proc, it will cancel the procurement
        made by these moves.
        """
        for rec in self:
            # cancel all the previous order
            ids = rec.move_raw_ids.ids
            rec.move_raw_ids.action_cancel()
            if cancel_linked_proc:
                linked_procs = self.env['procurement.order'].search(
                    [('move_dest_id', 'in', ids),
                     ('state', 'not in', ('done', 'cancel'))])
                linked_procs.cancel()

    @api.multi
    def rebuild_raw_move_ids(self, with_assign=True):
        """(re)Generate raw moves.

        It will generate raw moves for the MO.
        Typical usecase is call this func after the MO has been
        moved in another location. You then want to supply this MO
        from its new location.
        with_assign : kind of mrp_auto_assign
        """
        for rec in self:
            factor = rec.product_uom_id._compute_quantity(
                rec.product_qty,
                rec.bom_id.product_uom_id) / rec.bom_id.product_qty
            boms, lines = rec.bom_id.explode(
                rec.product_id, factor,
                picking_type=rec.bom_id.picking_type_id)

            rec._generate_raw_moves(lines)
            rec._adjust_procure_method()
            rec.move_raw_ids.filtered(
                lambda x: x.state == 'draft'
            ).action_confirm()
            if with_assign:
                rec.action_assign()

    @api.multi
    def update_moves_after_production(self, supplier, supplier_wh,
                                      supplier_loc):
        # Modify outgoing move and create a second one herebefore
        # It's easier to add new move before the existing one
        moves_out = self.env['stock.move']
        moves_out_dest = self.env['stock.move']
        old_pickings = self.env['stock.picking']
        for finish_move in self.move_finished_ids:
            if not finish_move.move_dest_id:
                # no shipping, probably created
                # for stock
                continue
            # TODO maybe need to handle last delivery move. (coming from SO)
            move_out = finish_move.move_dest_id
            move_out_dest = move_out.move_dest_id
            moves_out |= move_out
            moves_out_dest |= move_out_dest

            old_pickings |= move_out.picking_id
            # TODO update procurements?
            move_out.picking_id = False
            move_out.location_id = supplier_loc.id
            move_out.warehouse_id = supplier_wh.id
            move_out.picking_type_id = supplier_wh.out_type_id.id
            move_out.assign_picking()

            if move_out_dest:
                old_pickings |= move_out_dest.picking_id
                move_out_dest.picking_id = False
                move_out_dest.partner_id = supplier.id
                move_out_dest.assign_picking()
        for picking in old_pickings:
            if not picking.move_lines:
                picking.unlink()
        return moves_out, moves_out_dest

    @api.multi
    def get_expedition_and_reception_moves(self):
        self.ensure_one()
        moves_out = self.env['stock.move']
        moves_out_dest = self.env['stock.move']
        for finish_move in self.move_finished_ids:
            move_out = finish_move.move_dest_id
            move_out_dest = move_out.move_dest_id
            moves_out |= move_out
            moves_out_dest |= move_out_dest
        return moves_out, moves_out_dest

    # @api.multi
    # def write(self, vals):
    #     """Propagate date_planned start to previous move."""

    #     # lorsqu'on change la date de la mo
    #     #  on change la date de reception associée
    #     # est-ce vraiment utile ??
    #     res = super(MrpProduction, self).write(vals)
    #     if 'date_planned_start' in vals:
    #         inter_wh = self.env.ref('stock.stock_location_inter_wh')

    #         for move_in in self.move_raw_ids.filtered(
    #             lambda r: r.state not in ['done', 'cancel']
    #         ):
    #             for previous_move in move_in.move_orig_ids:
    #                 if previous_move.location_id != inter_wh:
    #                     _logger.warning('precedent non concernee')
    #                     continue
    #                 if len(move_in.move_orig_ids) > 1:
    #                     _logger.warning('devrait pas arriver !')
    #                 previous_move.date_expected = move_in.date_expected
    #                 _logger.info('date du precedent pickng changee')
    #         _logger.info('pour le moment on fait pas les move out')
    #     return res
