# Copyright 2024 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

try:
    from vcr_unittest import VCRMixin
except ImportError:
    VCRMixin = None


class TestCertificateApi(TransactionCase, VCRMixin):
    def setUp(self):
        super().setUp()
        warehouse = self.env.ref("stock.warehouse0")
        contact = self.env["res.partner"].create(
            {
                "name": "Jhon Doe",
                "email": "jhon.doe@akretion.com",
                "mobile": "+33699999999",
            }
        )
        self.desktop = self.env["desktop"].create(
            {
                "location_id": warehouse.id,
                "name": "TEST",
                "certificate_partner_id": contact.id,
            }
        )
        self._set_mpki_api()

    def _set_mpki_api(self):
        ir_config_model = self.env["ir.config_parameter"].sudo()
        # This is the IP address of the docker host
        ir_config_model.set_param("mpki_api_url", "http://172.17.0.1:8000/certs")
        ir_config_model.set_param("mpki_api_user", "abilis")
        ir_config_model.set_param("mpki_api_password", "TESTTESTTESTTEST")

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "once",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    def test_generate_certificate(self):
        self.assertEqual(len(self.desktop.certificate_ids), 0)
        self.desktop.generate_certificate()
        self.assertEqual(len(self.desktop.certificate_ids), 1)
        certificate1 = self.desktop.certificate_ids
        self.desktop.generate_certificate()
        self.assertEqual(len(self.desktop.certificate_ids), 2)
        for cert in self.desktop.certificate_ids:
            self.assertEqual(cert.sent_to_email, "jhon.doe@akretion.com")
            self.assertEqual(cert.sent_to_phone, "+33699999999")
            self.assertEqual(cert.revoked, False)
        certificate1.action_archive()
        self.assertEqual(certificate1.revoked, True)
        with self.assertRaises(UserError):
            certificate1.action_unarchive()
        self.assertEqual(len(self.desktop.certificate_ids), 1)
