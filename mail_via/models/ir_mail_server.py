# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrMail_Server(models.Model):
    _inherit = 'ir.mail_server'

    def build_email(self, email_from, email_to, subject, body, **kwargs):
        if self._context.get('sender_is_via'):
            via = self.env['ir.config_parameter'].get_param("mail.via.alias")
            domain = self.env['ir.config_parameter'].get_param(
                "mail.catchall.domain")
            original_from = email_from.replace('<', '"').replace('>', '"')
            email_from = '%s <%s@%s>' % (original_from, via, domain)
        return super(IrMail_Server, self).build_email(
            email_from, email_to, subject, body, **kwargs)
