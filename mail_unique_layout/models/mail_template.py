# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        notif_layout=False,
    ):
        record = self.env[self.model].browse(res_id)
        return super().send_mail(
            res_id,
            force_send=force_send,
            raise_exception=raise_exception,
            email_values=email_values,
            notif_layout=record._get_mail_layout(),
        )
