# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrActionsActProxy(models.Model):
    _name = "ir.actions.act_proxy"
    _description = "Action Proxy"
    _inherit = "ir.actions.actions"
    _table = "ir_actions"

    type = fields.Char(default="ir.actions.act_proxy")

    def _get_readable_fields(self):
        return super()._get_readable_fields() | {
            "action_list",
        }
