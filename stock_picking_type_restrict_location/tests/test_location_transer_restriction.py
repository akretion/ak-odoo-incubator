# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError


class TestTransferLocationRestriction(TransactionCase):
    def setUp(self):
        super(TestTransferLocationRestriction, self).setUp()

    def test_transfer_restriction(self):
        picking_type = self.env.ref("stock.picking_type_internal")
        location = self.env.ref("stock.stock_location_stock")
        dest_loc = self.env.ref("stock.stock_location_output")
        product = self.env.ref("product.product_product_35")
        move = self.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "name": product.name,
                "location_id": location.id,
                "location_dest_id": dest_loc.id,
                "picking_type_id": picking_type.id,
            }
        )
        self.env["stock.location.transfer.incompatibility"].create(
            {
                "picking_type_id": picking_type.id,
                "location1_id": location.id,
                "location2_id": dest_loc.id,
            }
        )
        move.action_confirm()
        with self.assertRaises(UserError):
            move.action_done()
