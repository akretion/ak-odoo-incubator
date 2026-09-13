# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Users(models.Model):
    _name = "res.users"
    _inherit = ["res.users", "res.users.role.description"]

    recursive_model_access_ids = fields.Many2many(
        comodel_name="ir.model.access",
        compute="_compute_model_access_ids",
        string="Access Rights",
    )

    def _get_all_implied_groups(self):
        self.ensure_one()
        groups = self.groups_id
        to_process = self.groups_id

        while to_process:
            groups |= to_process
            to_process = to_process.implied_ids - groups

        return groups

    def _compute_model_access_ids(self):
        for rec in self:
            rec.recursive_model_access_ids = (
                rec._get_all_implied_groups().model_access.ids
            )
