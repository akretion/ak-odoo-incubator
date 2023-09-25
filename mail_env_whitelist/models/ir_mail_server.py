# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import api, models
from odoo.tools.config import config


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def send_email(self, message, *args, **kwargs):
        if config["running_env"] != "prod":
            whitelist = self.env["ir.config_parameter"].get_param(
                "mail_env_whitelist.test_env_email_to_whitelist"
            )
            for email in message["To"].split(";"):
                email = re.search("<(.*)>", email).group(1)
                if email not in whitelist:
                    continue
                else:
                    super().send_email(message, *args, **kwargs)
