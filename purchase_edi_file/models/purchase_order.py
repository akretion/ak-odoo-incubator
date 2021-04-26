#  Copyright (C) 2021 Akretion (http://www.akretion.com).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_approve(self, force=False):
        res = super().button_approve(force=force)
        self.generate_and_send_edi_files()
        return res

    def _should_send_edi_file(self):
        self.ensure_one()
        partner = self.partner_id
        edi_transfer = (
            partner.edi_storage_backend_id
            or partner.edi_mail_template_id
            or partner.edi_transfer_method == "manual"
            and "manual"
            or False
        )
        return edi_transfer and True or False

    def generate_and_send_edi_files(self):
        for purchase in self:
            if not purchase._should_send_edi_file():
                continue
            partner = purchase.partner_id
            profiles_lines = purchase.order_line._get_lines_by_profiles(partner)
            attachments = self.env["ir.attachment"]
            for profile, records in profiles_lines.items():
                if not records and not partner.edi_empty_file:
                    continue
                attachments |= profile.get_attachment(
                    records, res_id=purchase.id, res_model=self._name
                )
            if attachments:
                partner.send_supplier_edi_attachments(attachments, purchase=purchase)
