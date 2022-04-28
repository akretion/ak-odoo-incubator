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
        return partner.edi_transport_config_id and True or False

    def generate_and_send_edi_files(self):
        for purchase in self:
            if not purchase._should_send_edi_file():
                continue
            partner = purchase.partner_id
            profiles_lines = purchase.order_line._get_lines_by_profiles(partner)
            attachments = self.env["ir.attachment"]
            attachment_profiles = {}
            for profile, records in profiles_lines.items():
                if not records:
                    continue
                attachments |= profile.get_attachment(
                    records, res_id=purchase.id, res_model=self._name
                )
                attachment_profiles[profile] = attachments
            if not attachment_profiles:
                continue
            attachment_by_transfer = {}
            # attachment could be send at different location depending on the profile
            # group all attachment per transfer method and then send it (the goal beeing
            # to send only one email if multiple file must be sent per mail)
            for profile, attachments in attachment_profiles.items():
                transfer_config = (
                    profile.partner_edi_transport_config_ids.filtered(
                        lambda x: x.partner_id == self.partner_id
                    ).edi_transport_config_id
                    or partner.edi_transport_config_id
                )
                if transfer_config not in attachment_by_transfer:
                    attachment_by_transfer[transfer_config] = self.env["ir.attachment"]
                attachment_by_transfer[transfer_config] |= attachments

            for transfer_config, attachments in attachment_by_transfer.items():
                partner.send_supplier_edi_attachments(
                    attachments, config=transfer_config, purchase=purchase
                )
