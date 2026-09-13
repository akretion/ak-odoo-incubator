# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPickingRestrictQtyEditable(TransactionCase):
    def setUp(self):
        super().setUp()

        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        self.picking_type = self.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type",
                "code": "internal",
                "sequence_code": "INT",
                "warehouse_id": self.env.ref("stock.warehouse0").id,
            }
        )

        self.picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.env["stock.location"]
                .search([("usage", "=", "internal")], limit=1)
                .id,
                "location_dest_id": self.env["stock.location"]
                .search([("usage", "=", "internal")], limit=1)
                .id,
            }
        )

        self.move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": 10.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
                "picking_id": self.picking.id,
            }
        )

    def test_is_quantity_done_editable_in_done_state(self):
        self.move.state = "done"
        self.assertFalse(self.move.is_quantity_done_editable)

    def test_initial_demand_not_editable_if_sale_line(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.partner_admin").id,
            }
        )
        sale_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 5,
                "product_uom": self.product.uom_id.id,
                "price_unit": 10,
            }
        )

        self.move.sale_line_id = sale_line.id
        self.assertFalse(self.move.is_initial_demand_editable)

    def test_initial_demand_not_editable_if_done(self):
        self.move.state = "done"
        self.move._compute_is_initial_demand_editable()
        self.assertFalse(self.move.is_initial_demand_editable)

    def test_quantity_done_set_raises_if_done(self):
        self.move.state = "done"
        with self.assertRaises(UserError):
            self.move.quantity_done = 100.0

    def test_quantity_done_set_allowed_if_not_done(self):
        self.move.state = "assigned"
        self.move.quantity_done = 5.0
