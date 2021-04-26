# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import SavepointCase


class TestPurchaseEdiFile(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.po = cls.env.ref("purchase_edi_file.demo_edi_po")

    def test_partner_edi_profiles(self):
        self.assertEqual(len(self.supplier.edi_purchase_profile_ids), 3)

    def test_export_external_location(self):
        self.po.button_approve()
        attachments = self.env["attachment.queue"].search(
            [("res_id", "=", self.po.id), ("res_model", "=", "purchase.order")]
        )
        self.assertEqual(len(attachments), 2)
        self.assertEqual(attachments[0].file_type, "export")

    def test_export_by_mail(self):
        template = self.env["mail.template"].create(
            {
                "name": "test EDI template",
                "model_id": self.env.ref("purchase.model_purchase_order").id,
                "subject": "EDI files",
                "email_from": "dummy@dummy.com",
                "email_to": "dummyto@dummy.com",
            }
        )
        self.supplier.write(
            {"edi_transfer_method": "mail", "edi_mail_template_id": template.id}
        )
        self.po.button_approve()
        mail = self.env["mail.mail"].search(
            [("res_id", "=", self.po.id), ("model", "=", "purchase.order")]
        )
        self.assertEqual(len(mail), 1)
        self.assertEqual(len(mail.attachment_ids), 2)

    def test_export_with_empty_files(self):
        self.supplier.write({"edi_empty_file": True})
        self.po.button_approve()
        attachments = self.env["attachment.queue"].search(
            [("res_id", "=", self.po.id), ("res_model", "=", "purchase.order")]
        )
        self.assertEqual(len(attachments), 3)
