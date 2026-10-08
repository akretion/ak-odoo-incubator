# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import AccessDenied
from odoo.tests import TransactionCase, tagged
from odoo.tools import config

from ..hooks import pre_init_hook


@tagged("post_install", "-at_install")
class TestNonProd(TransactionCase):
    def _options(self, running_env):
        return patch.dict(
            config.options,
            {
                "running_env": running_env,
                "test_enable": False,
                "partner_db_instance_master": "project_master",
                "partner_db_instance_password": "secret",
                "dbfilter": r"^project_%d$",
            },
        )

    def test_hook_non_prod_skips_database_name_check(self):
        for running_env in ("dev", "ci"):
            with self._options(running_env):
                # the test database is not the master one: no error
                pre_init_hook(self.env)

    def test_hook_prod_requires_master_database(self):
        with self._options("prod"), self.assertRaises(AccessDenied):
            pre_init_hook(self.env)

    def test_instance_url(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "web.base.url", "https://project_master.example.com"
        )
        partner = self.env["res.partner"].create({"name": "Ferme"})
        with self._options("prod"):
            instance = self.env["res.partner.instance"].create(
                {"partner_id": partner.id, "subdomain": "ferme"}
            )
            self.assertEqual(instance.url, "https://ferme.example.com")
        with self._options("dev"):
            instance.invalidate_recordset(["url"])
            self.assertEqual(instance.url, "https://project_ferme.example.com")
