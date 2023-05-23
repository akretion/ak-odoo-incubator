# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.tests import SavepointCase as TransactionCase


class TestTrackerTrace(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        from .models import ResPartner

        cls.loader.update_registry((ResPartner,))

        cls.env.ref("base.res_partner_12")._onchange_state()

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestTrackerTrace, cls).tearDownClass()

    def test_tracker_trace(self):

        method_tracker = "fonction_tracker_test"  #'name of the method called by the _onchange_method'
        method_onchange = "_onchange_state"  #'name of the _onchange_method'
        log = self.env["tracker.code.info"].search(
            [("log_trace", "=", method_onchange)]
        )

        function = self.env["tracker.code.info"].search(
            [("function_name", "=", method_tracker)], order="id desc", limit=1
        )

        self.assertTrue(function)
        self.assertTrue(function.user)
        self.assertIn(method_onchange, function.log_trace)
