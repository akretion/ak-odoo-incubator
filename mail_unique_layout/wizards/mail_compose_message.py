# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):
        record = self.env[self.model].browse(self.res_id)
        self = self.with_context(custom_layout=record._get_mail_layout())
        return super().send_mail(auto_commit=auto_commit)
