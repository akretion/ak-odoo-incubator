# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):
        self = self.with_context(
            custom_layout=self.env["mail.thread"]._get_unique_layout_ref()
        )
        return super().send_mail(auto_commit=auto_commit)
