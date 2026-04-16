# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestTrackingSaleReconfirmation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_product_5")
        for model_name, fnames in [
            ("sale.order", ["client_order_ref"]),
            ("sale.order.line", ["product_uom_qty"]),
        ]:
            ir_model = cls.env["ir.model"].search([("model", "=", model_name)])
            ir_model.active_custom_tracking = True
            for fname in fnames:
                field = cls.env["ir.model.fields"].search(
                    [("model_id", "=", ir_model.id), ("name", "=", fname)]
                )
                field.custom_tracking = True
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 2,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        cls.order.action_confirm()
        cls.order.action_cancel()
        cls.order.action_draft()
        cls.tracking = cls.order.active_cancel_tracking_id

    def test_reset_to_draft_updates_tracking(self):
        self.assertEqual(self.tracking.state, "draft")
        self.assertTrue(self.tracking.draft_date)

    def test_reconfirm_closes_tracking(self):
        self.order.action_confirm()
        self.assertEqual(self.tracking.state, "done")
        self.assertTrue(self.tracking.confirm_date)
        self.assertFalse(self.order.active_cancel_tracking_id)

    def test_full_cycle_increments_count(self):
        self.order.action_confirm()
        self.assertEqual(self.order.cancel_tracking_count, 1)
        self.order.action_cancel()
        self.order.action_draft()
        self.order.action_confirm()
        self.assertEqual(self.order.cancel_tracking_count, 2)

    def test_order_field_change_recorded(self):
        self.order.write({"client_order_ref": "REF-001"})
        change = self.tracking.change_line_ids.filtered(
            lambda l: l.field_label
            == self.order._fields["client_order_ref"]
            .get_description(self.env)
            .get("string")
        )
        self.assertTrue(change)
        self.assertEqual(change.new_value, "REF-001")

    def test_line_qty_change_recorded(self):
        line = self.order.order_line[0]
        line.write({"product_uom_qty": 5})
        change = self.tracking.change_line_ids.filtered(
            lambda l: l.field_label
            == line._fields["product_uom_qty"].get_description(self.env).get("string")
        )
        self.assertTrue(change)
        self.assertEqual(change.new_value, "5.0")

    def test_line_added_recorded(self):
        self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": 50,
            }
        )
        change = self.tracking.change_line_ids.filtered(
            lambda l: l.field_label == "Line added"
        )
        self.assertTrue(change)

    def test_no_tracking_when_confirmed(self):
        self.order.action_confirm()
        count_before = len(self.tracking.change_line_ids)
        self.order.write({"client_order_ref": "SHOULD-NOT-TRACK"})
        self.assertEqual(len(self.tracking.change_line_ids), count_before)
