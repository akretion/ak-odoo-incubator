# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.tests import SavepointCase


class TestAutomaticSupplierDelay(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = cls.env.company.write({"incoming_shipment_number_delay": 2})
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.supplier = cls.env.ref("base.res_partner_1")
        cls.suppinfo = cls.env.ref("product.product_supplierinfo_19")

    def _create_validate_po_incoming_shipment(self, validation_date, ship_date):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "name": self.product.name,
                            "product_qty": 1,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        with freeze_time(validation_date):
            po.button_confirm()
        picking = po.picking_ids.with_context(skip_immediate=True)
        with freeze_time(ship_date):
            picking.move_lines.move_line_ids.qty_done = 1
            picking.button_validate()

    def test_automatic_date(self):
        # original supplierinfo is 4
        self._create_validate_po_incoming_shipment("2021-01-07", "2021-01-13")
        # unique reception => take this reception delay
        self.assertEqual(self.suppinfo.delay, 6)
        self._create_validate_po_incoming_shipment("2021-01-10", "2021-01-20")
        # 2 receptions take the average
        self.assertEqual(self.suppinfo.delay, 8)
        self._create_validate_po_incoming_shipment("2021-01-20", "2021-01-22")
        # 2 receptions take the last 2 average
        self.assertEqual(self.suppinfo.delay, 6)
