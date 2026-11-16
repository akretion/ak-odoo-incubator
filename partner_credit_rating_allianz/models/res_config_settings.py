# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allianz_env = fields.Selection(
        [("uat", "Test (UAT)"), ("prod", "Production")],
        string="Allianz Trade Environment",
        default="uat",
        config_parameter="allianz_trade.env",
    )
    allianz_api_key = fields.Char(
        string="Allianz Trade API Key", config_parameter="allianz_trade.api_key"
    )
    allianz_idp_base_uat = fields.Char(config_parameter="allianz_trade.idp_base_uat")
    allianz_idp_base_prod = fields.Char(config_parameter="allianz_trade.idp_base_prod")
    allianz_search_base_uat = fields.Char(
        config_parameter="allianz_trade.companysearch_base_uat"
    )
    allianz_search_base_prod = fields.Char(
        config_parameter="allianz_trade.companysearch_base_prod"
    )
    allianz_grade_base_uat = fields.Char(
        config_parameter="allianz_trade.gradecheck_base_uat"
    )
    allianz_grade_base_prod = fields.Char(
        config_parameter="allianz_trade.gradecheck_base_prod"
    )
    allianz_business_unit = fields.Char(
        string="Business Unit Code",
        config_parameter="allianz_trade.business_unit_code",
        help="Required by Grade Check, e.g. SFAC",
    )
    allianz_policy = fields.Char(
        string="Policy ID", config_parameter="allianz_trade.policy_id"
    )

    def action_allianz_test(self):
        self.ensure_one()
        self.set_values()
        self.env["credit.rating"]._allianz_token(force=True)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": _("Allianz Trade connection OK"),
                "type": "success",
            },
        }
