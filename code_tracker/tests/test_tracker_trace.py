# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.tests import SavepointCase


class TestTrackerTrace(SavepointCase):
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

        # Name of the _onchange_method and on the method called by the _onchange_method
        method_tracker = "fonction_tracker_test"
        method_onchange = "_onchange_state"

        function = self.env["tracker.code.info"].search(
            [("function_name", "=", method_tracker)], order="id desc", limit=1
        )

        self.assertTrue(function)
        self.assertTrue(function.user)
        self.assertIn(method_onchange, function.log_trace)
