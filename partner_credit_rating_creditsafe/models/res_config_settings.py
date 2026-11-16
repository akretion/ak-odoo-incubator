# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    creditsafe_env = fields.Selection(
        [("sandbox", "Test (Sandbox)"), ("prod", "Production")],
        string="Creditsafe Environment",
        default="sandbox",
        config_parameter="creditsafe.env",
    )
    creditsafe_username = fields.Char(config_parameter="creditsafe.username")
    creditsafe_password = fields.Char(config_parameter="creditsafe.password")

    def action_creditsafe_test(self):
        self.ensure_one()
        self.set_values()
        self.env["credit.rating"]._creditsafe_token(force=True)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": self.env._("Creditsafe connection OK"),
                "type": "success",
            },
        }
