# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools.config import config


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def send_email(self, message, *args, **kwargs):
        if config["running_env"] != "prod":
            whitelist = self.env["ir.config_parameter"].get_param(
                "mail_env_whitelist.test_env_email_to_whitelist"
            )
            if not whitelist:
                raise UserError(
                    _(
                        "Whitelist is not configured. Configure the following parameter "
                        "'mail_env_whitelist.test_env_email_to_whitelist'"
                    )
                )
            for key in ["To", "cc", "Bcc"]:
                if message[key]:
                    for email in message[key].split(";"):
                        match = re.search("<(.*)>", email)
                        if match:
                            # in case of full syntax "foo" <foo@exemple.org>
                            # extract the email
                            email = match.group(1)
                        email = email.lower()
                        if email not in whitelist:
                            raise UserError(
                                _("Test env: following mail is not allowed %s") % email
                            )
        return super().send_email(message, *args, **kwargs)
