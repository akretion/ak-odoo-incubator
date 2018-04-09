# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def update_locations(self, purchase):
        self.ensure_one()
        # TODO Add some check and raises to avoid big mess?
        subcontract_loc = purchase.partner_id.supplier_location_id
        subcontract_wh = self.env.ref(
            'mrp_subcontract_location.warehouse_supplier')
        subcontract_main_loc = subcontract_wh.lot_stock_id
        if self.location_src_id.id != subcontract_main_loc.id or \
                self.location_dest_id.id != subcontract_main_loc.id:
            return
        if not subcontract_loc:
            raise exceptions.ValidationError(
                _('No location configured on the subcontractor'))
#        previous_picking_ids = []
        for raw_line in self.move_raw_ids:
            ancestors = raw_line.get_ancestors()
            if not (ancestors and ancestors[0].production_id):
                raw_line.write({'location_id': subcontract_loc.id})
#                if ancestors and ancestors[0].picking_id:
#                    picking = ancestors[0].picking_id
#                    if (picking.state not in ('done', 'cancel') and
#                            picking.id not in previous_picking_ids):
#                        ancestor_loc = picking.location_dest_id
#                        if ancestor_loc.id == subcontract_main_loc.id:
#                            picking.write(
#                                {'location_dest_id': subcontract_main_loc.id})
#                            previous_picking_ids.append(picking.id)
        self.move_finished_ids.write({'location_dest_id': subcontract_loc.id})
        for move in self.move_finished_ids:
            dest = move.move_dest_id
            # Could be set by next chained MO
            if dest and dest.location_dest_id.id != subcontract_loc.id:
                move.move_dest_id.write(
                    {'location_id': subcontract_loc.id})
