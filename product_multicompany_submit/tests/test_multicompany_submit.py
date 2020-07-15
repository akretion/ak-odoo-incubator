#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from .common import MulticompanySubmitCase
from odoo.exceptions import AccessError


class TestMulticompanySubmit(MulticompanySubmitCase):
    def _helper_check_permissions(self, has_permission, no_permission):
        for el in has_permission:
            user = getattr(self, "user_" + el).id
            self.product.sudo(user).read(["name"])
        for el in no_permission:
            user = getattr(self, "user_" + el).id
            with self.assertRaises(AccessError):
                self.product.sudo(user).read(["name"])

    def test_permissions_not_submitted(self):
        """ NOT SUBMITTED product:
        accessible to submitter,
        inaccessible to approver, other user """
        self.product.state_multicompany_submit = "not_submitted"
        self._helper_check_permissions(("submitter"), ("approver", "other"))

    def test_permissions_pending(self):
        """ PENDING product:
        accessible to approver, submitter
        inaccessible to other user """
        self._helper_check_permissions(("approver", "submitter"), ("other"))

    def test_permissions_approved(self):
        """ APPROVED product:
        accessible to everyone """
        self.product.action_make_multicompany()
        self._helper_check_permissions(("approver", "submitter", "other"), ())

    def test_permissions_refused(self):
        """ REFUSED product:
        accessible to approver, submitter
        inaccessible to other user """
        self.product.button_multicompany_refuse()
        self._helper_check_permissions(("approver", "submitter"), ("other"))

    def test_workflow_accept(self):
        self.product.button_multicompany_approve()
        self.assertEqual(self.product.state_multicompany_submit, "approved")

    def test_workflow_refuse(self):
        self.product.button_multicompany_refuse()
        self.assertEqual(self.product.state_multicompany_submit, "refused")

    def test_workflow_cancel(self):
        self.product.button_multicompany_cancel()
        self.assertEqual(self.product.state_multicompany_submit, "not_submitted")
