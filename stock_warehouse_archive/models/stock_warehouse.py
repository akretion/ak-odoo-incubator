# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


LOCATION_FIELDS = [
    "view_location_id",
    "lot_stock_id",
    "wh_input_stock_loc_id",
    "wh_qc_stock_loc_id",
    "wh_pack_stock_loc_id",
    "wh_output_stock_loc_id",
    "lot_rma_id",
    "sam_loc_id",
    "pbm_loc_id",
    "repair_location_id",
]


class StockWarehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["mail.thread", "stock.warehouse"]

    def _cancel_pickings(self, pickings, messages):
        for picking in pickings:
            messages.append(
                _("%(name)s created %(create_date)s")
                % dict(
                    name=picking.name,
                    create_date=picking.create_date,
                )
            )
            picking.action_cancel()

    def _cancel_moves(self, moves, messages):
        for move in moves:
            messages.append(
                _("%(qty)s X %(name)s created %(create_date)s")
                % dict(
                    qty=move.product_qty,
                    name=move.name,
                    create_date=move.create_date,
                )
            )
            move._action_cancel()

    def _action_cancel_related_move_from_picking_type(self):
        messages = []
        picking_types = (
            self.env["stock.picking.type"]
            .with_context(active_test=False)
            .search([("warehouse_id", "=", self.id)])
        )

        for picking_type in picking_types:
            pickings = self.env["stock.picking"].search(
                [
                    ("picking_type_id", "=", picking_type.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )

            if pickings:
                messages += ["", _("Cancel picking with type %s") % picking_type.name]
                self._cancel_pickings(pickings, messages)

            moves = self.env["stock.move"].search(
                [
                    ("picking_type_id", "=", picking_type.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            if moves:
                messages += ["", _("Cancel Move with type %s") % picking_type.name]
                self._cancel_moves(moves, messages)
        return messages

    def _action_cancel_related_move_from_location(self, locations):
        messages = []
        for location in locations:
            pickings = self.env["stock.picking"].search(
                [
                    ("location_id", "=", location.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            if pickings:
                messages += ["", _("Cancel Picking with source %s") % location.name]
                self._cancel_pickings(pickings, messages)

            pickings = self.env["stock.picking"].search(
                [
                    ("location_dest_id", "=", location.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )

            if pickings:
                messages += [
                    "",
                    _("Cancel Picking with destination %s") % location.name,
                ]
                self._cancel_pickings(pickings, messages)

            moves = self.env["stock.move"].search(
                [
                    ("location_id", "=", location.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            if moves:
                messages += ["", _("Cancel Move with source %s") % location.name]
                self._cancel_moves(moves, messages)

            moves = self.env["stock.move"].search(
                [
                    ("location_dest_id", "=", location.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            if moves:
                messages += ["", _("Cancel Move with destination %s") % location.name]
                self._cancel_moves(moves, messages)
        return messages

    def _action_purge_with_inventory(self, locations):
        for location in locations:
            if location.usage == "internal":
                inventory = self.env["stock.inventory"].create(
                    {
                        "name": _("Archive %(warehouse)s %(location)s")
                        % dict(warehouse=self.name, location=location.name),
                        "location_ids": [(6, 0, [location.id])],
                        "company_id": self.company_id.id,
                    }
                )
                inventory.action_start()

                # Compatibility with stock_inventory_location_state
                if "sub_location_ids" in inventory._fields:
                    inventory.sub_location_ids.state = "done"
                inventory._action_done()

    def force_archive(self):

        # Add the key in the context so you can adapt custom module behaviour
        # if needed
        self = self.with_context(archive_warehouse=True)

        for warehouse in self:
            messages = ["Force to archive warehouse"]
            messages += warehouse._action_cancel_related_move_from_picking_type()

            locations = self.env["stock.location"]
            for field in LOCATION_FIELDS:
                if field in warehouse._fields:
                    locations |= self[field]

            messages += warehouse._action_cancel_related_move_from_location(locations)
            warehouse._action_purge_with_inventory(locations)
            warehouse.message_post(body="<br/>".join(messages))
            warehouse.active = False
