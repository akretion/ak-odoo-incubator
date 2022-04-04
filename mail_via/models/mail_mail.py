# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        incoming_mails = self.filtered("fetchmail_server_id")
        super(MailMail, incoming_mails.with_context(sender_is_via=True)).send(
            auto_commit=auto_commit, raise_exception=raise_exception
        )
        normal_mails = self.filtered(lambda s: not s.fetchmail_server_id)
        super(MailMail, normal_mails).send(
            auto_commit=auto_commit, raise_exception=raise_exception
        )
        return True
