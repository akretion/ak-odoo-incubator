# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.addons.mail.tests.common import MockEmail
from odoo.addons.purchase_sale_inter_company.tests.test_inter_company_purchase_sale import (
    TestPurchaseSaleInterCompany,
)


class TestPurchaseRequirementProposal(MockEmail, TestPurchaseSaleInterCompany):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.call_for_proposal_type = cls.env.ref(
            "purchase_requisition_proposal.call_for_proposals_type"
        )

        cls.company_a.so_from_po = True
        cls.company_a.warehouse_id = cls.warehouse_a
        cls.company_a.requisition_intercompany_partner_ids = cls.user_company_a
        cls.company_b.requisition_intercompany_partner_ids = cls.user_company_b

        cls.partner_company_a.email = "email_a.email@email.com"
        cls.partner_company_b.email = "email_b.email@email.com"

        cls.product_uom_id = cls.env.ref("uom.product_uom_unit")

        cls.product_1 = cls.product.create({"name": "product_1"})
        cls.product_2 = cls.product.create({"name": "product_2"})

        cls.call_for_proposal_type.multi_company_selection = "all"

        cls.line1 = (
            0,
            0,
            {
                "product_id": cls.product_1.id,
                "product_qty": 10,
                "product_uom_id": cls.product_uom_id.id,
                "price_unit": 100,
            },
        )
        cls.line2 = (
            0,
            0,
            {
                "product_id": cls.product_2.id,
                "product_qty": 20,
                "product_uom_id": cls.product_uom_id.id,
                "price_unit": 200,
            },
        )

        cls.call = cls.env["purchase.requisition"].create(
            {
                "type_id": cls.call_for_proposal_type.id,
                "date_end": "2222-06-15",
                "schedule_date": "2222-06-21",
                "line_ids": [cls.line1, cls.line2],
            }
        )

        cls.call._onchange_schedule_date()
        cls.call_line1 = cls.call.line_ids[0]
        cls.call_line2 = cls.call.line_ids[1]

        cls.call.action_in_progress()
        cls.call_line1.with_user(cls.user_company_a).proposal_validation()
        cls.proposal_1 = cls.call_line1.proposal_line_ids[0]

    def test_1_call_for_proposal_type(self):
        self.assertEqual(len(self.call.company_to_call_ids), 3)
        self.call_for_proposal_type.multi_company_selection = "selected"
        self.call_for_proposal_type.company_to_call_ids = self.company_b
        self.call2 = self.env["purchase.requisition"].create(
            {
                "type_id": self.call_for_proposal_type.id,
                "date_end": "2222-06-15",
                "schedule_date": "2222-06-21",
                "line_ids": [self.line1],
            }
        )
        self.assertEqual(len(self.call2.company_to_call_ids), 1)

    def test_2_call_for_proposal_settings(self):
        self.assertEqual(self.call.schedule_date, self.call_line1.schedule_date)
        self.assertTrue(self.call_line1.proposal_line_count, 1)

    def test_3_validate_call_and_send_mail(self):
        email = self.call.action_call_for_proposal_send()
        composer = (
            self.env["mail.compose.message"].with_context(email["context"]).create({})
        )
        with self.mock_mail_gateway():
            composer.action_send_mail()
        mail = self.env["mail.mail"].search([("model", "=", "purchase.requisition")])
        self.assertTrue(mail)
        # self.assertIn(
        #     "The Agreement Deadline is", mail.body
        # )

    def test_4_proposal_accept(self):
        self.assertEqual(self.call_line1.proposal_line_count, 1)
        self.assertEqual(self.call_line1.product_qty, self.proposal_1.qty_proposed)
        self.assertEqual(self.call_line1.schedule_date, self.proposal_1.date_planned)
        self.assertEqual(self.company_a.partner_id, self.proposal_1.partner_id)
        self.call_line1.with_company(self.company_b).proposal_validation()
        self.assertEqual(self.call_line1.proposal_line_count, 1)

    def test_5_proposal_duplicate_and_remove(self):
        self.proposal_1.duplicate_line()
        self.assertEqual(len(self.call_line1.proposal_line_ids), 2)
        self.proposal_1.remove_line()
        self.assertEqual(len(self.call_line1.proposal_line_ids), 1)

    def test_6_proposal_check_line(self):
        self.assertEqual(self.proposal_1.date_check, "respected")
        self.assertEqual(self.proposal_1.qty_check, "not_enough")
        self.proposal_1.date_planned = "2222-06-23"
        self.assertEqual(self.proposal_1.date_check, "not_respected")
        self.proposal_1.qty_planned = 10
        self.assertEqual(self.proposal_1.qty_check, "enough")

    def test_7_proposal_to_call(self):
        self.assertEqual(self.call_line1.date_check, "none")
        self.assertEqual(self.call_line1.qty_check, "not_enough")
        self.proposal_1.qty_planned = 10
        self.proposal_1.date_planned = "2222-06-20"
        self.assertEqual(self.call_line1.date_check, "respected")
        self.assertEqual(self.call_line1.qty_check, "enough")
        self.proposal_1.date_planned = "2222-06-23"
        self.assertEqual(self.call_line1.date_check, "not_respected")

    def test_8_create_rfq(self):
        self.call.action_call_for_proposal_send()
        self.call_line2.with_company(self.company_b).proposal_validation()
        with self.assertRaises(ValidationError) as m:
            self.call.action_create_quotations()
        self.assertIn("You need to select at least one proposition", m.exception.args[0]
            )
        self.proposal_1.qty_planned = 10
        self.call_line2.proposal_line_ids[0].qty_planned = 20
        self.call.action_create_quotations()
        self.assertEqual(len(self.call.purchase_ids), 2)
        self.assertEqual(self.call.purchase_ids[0].partner_id, self.partner_company_a)
        self.assertEqual(self.call.purchase_ids[1].partner_id, self.partner_company_b)
        pol1, pol2 = self.call.purchase_ids.order_line
        self.assertEqual(pol1.product_qty, self.call_line1.qty_planned)
        self.assertEqual(pol2.product_qty, self.call_line2.qty_planned)
        self.assertEqual(pol1.requirement_proposal_id, self.proposal_1)
        self.assertEqual(
            pol2.requirement_proposal_id, self.call_line2.proposal_line_ids[0]
        )

        self.call.purchase_ids.button_confirm()
        self.assertEqual(self.call_line1.qty_ordered, self.call_line1.qty_planned)
        self.assertEqual(self.call_line2.qty_ordered, self.call_line2.qty_planned)

    def test_9_related_sale(self):
        self.call.action_call_for_proposal_send()
        self.call_line2.with_company(self.company_b).proposal_validation()
        self.proposal_1.qty_planned = 10
        self.call_line2.proposal_line_ids[0].qty_planned = 20
        self.call.action_create_quotations()
        self.call.purchase_ids[0].with_user(self.env.user).button_confirm()
        self.call.purchase_ids[1].with_user(self.env.user).button_confirm()
        so_a = (
            self.env["sale.order"]
            .with_company(self.company_a)
            .search([("purchase_requisition_id", "=", self.call.id)])
        )
        self.assertIn(self.proposal_1.id, so_a.order_line.requirement_proposal_id.ids)
        so_b = (
            self.env["sale.order"]
            .with_company(self.company_b)
            .search([("purchase_requisition_id", "=", self.call.id)])
        )
        self.assertIn(
            self.call_line2.proposal_line_ids[0].id,
            so_b.order_line.requirement_proposal_id.ids,
        )
        self.assertEqual(so_b.order_line.mapped("price_unit"), [200.0, 100.0])
