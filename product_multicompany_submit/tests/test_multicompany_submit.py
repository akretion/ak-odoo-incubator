# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import AccessError


class TestMulticompanySubmit(common.TransactionCase):
    def setUp(self):
        super(TestMulticompanySubmit, self).setUp()
        # active multicompany
        self.env.ref("product.product_comp_rule").active = True

        self.company_approver = self.env["res.company"].create(
            {"name": "company of approver"}
        )
        self.company_submitter = self.env["res.company"].create(
            {"name": "company of submitter"}
        )
        self.company_other = self.env["res.company"].create(
            {"name": "company of other user"}
        )

        self.user_approver = self.env["res.users"].create(
            {
                "name": "approver",
                "login": "approver",
                "company_ids": self.company_approver.ids,
                "company_id": self.company_approver.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.ref(
                                "product_multicompany_submit."
                                "group_multicompany_product_approve"
                            ),
                            self.ref("base.group_user"),
                        ],
                    )
                ],
            }
        )

        self.user_submitter = self.env["res.users"].create(
            {
                "name": "submitter",
                "login": "submitter",
                "company_ids": self.company_submitter.ids,
                "company_id": self.company_submitter.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.ref(
                                "product_multicompany_submit."
                                "group_multicompany_product_submit"
                            ),
                            self.ref("base.group_user"),
                        ],
                    )
                ],
            }
        )

        self.user_other = self.env["res.users"].create(
            {
                "name": "other user",
                "login": "other user",
                "company_ids": self.company_other.ids,
                "company_id": self.company_other.id,
                "groups_id": [(6, 0, [self.ref("base.group_user")],)],
            }
        )

        self.product = self.env["product.template"].create(
            {"name": "some product", "company_id": self.company_submitter.id}
        )

    def test_permissions(self):
        self.assertEqual(
            self.product.state_multicompany_submit, "not_submitted"
        )
        self.assertEqual(
            self.product.multicompany_origin_company_id, self.company_submitter
        )
        self.assertEqual(self.product.company_id, self.company_submitter)

        # NOT SUBMITTED permissions: approver, other user should not have them
        with self.assertRaises(AccessError):
            self.env["product.template"].sudo(self.user_approver.id).browse(
                self.product.ids
            ).read(["name"])
        with self.assertRaises(AccessError):
            self.env["product.template"].sudo(self.user_other).browse(
                self.product.ids
            ).read(["name"])

        # NOT SUBMITTED permissions: submitter should have them
        self.env["product.template"].sudo(self.user_submitter).browse(
            self.product.ids
        ).read(["name"])

        # PENDING permissions: approver should have them
        self.product.state_multicompany_submit = "pending_approval"
        self.env["product.template"].sudo(self.user_approver).browse(
            self.product.ids
        ).read(["name"])

        # PENDING permissions: other user should still not have them
        with self.assertRaises(AccessError):
            self.product.state_multicompany_submit = "pending_approval"
            self.env["product.template"].sudo(self.user_other).browse(
                self.product.ids
            ).read(["name"])

        # APPROVED permissions: everyone
        self.product.button_multicompany_approve()
        self.assertEqual(self.product.company_id.ids, [])
        self.env["product.template"].sudo(self.user_approver).browse(
            self.product.ids
        ).read(["name"])
        self.env["product.template"].sudo(self.user_submitter).browse(
            self.product.ids
        ).read(["name"])
        self.env["product.template"].sudo(self.user_other).browse(
            self.product.ids
        ).read(["name"])

    def test_workflow_accept(self):
        self.assertEqual(
            self.product.state_multicompany_submit, "not_submitted"
        )
        self.product.button_multicompany_submit()
        self.assertEqual(
            self.product.state_multicompany_submit, "pending_approval"
        )
        self.product.button_multicompany_approve()
        self.assertEqual(self.product.state_multicompany_submit, "approved")

    def test_workflow_refuse(self):
        self.assertEqual(
            self.product.state_multicompany_submit, "not_submitted"
        )
        self.product.button_multicompany_submit()
        self.assertEqual(
            self.product.state_multicompany_submit, "pending_approval"
        )
        self.product.button_multicompany_refuse()
        self.assertEqual(self.product.state_multicompany_submit, "refused")

    def test_workflow_cancel(self):
        self.assertEqual(
            self.product.state_multicompany_submit, "not_submitted"
        )
        self.product.button_multicompany_submit()
        self.assertEqual(
            self.product.state_multicompany_submit, "pending_approval"
        )
        self.product.button_multicompany_cancel()
        self.assertEqual(
            self.product.state_multicompany_submit, "not_submitted"
        )
