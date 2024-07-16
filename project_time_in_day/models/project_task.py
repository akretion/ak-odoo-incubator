# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    planned_days = fields.Float(compute="_compute_planned_days", store=True)
    remaining_days = fields.Float(compute="_compute_remaining_days", store=True)
    effective_days = fields.Float(compute="_compute_effective_days", store=True)

    @api.depends("planned_hours", "project_id.hour_uom_id")
    def _compute_planned_days(self):
        for record in self:
            record.planned_days = record.project_id.convert_hours_to_days(
                record.planned_hours
            )

    @api.depends("remaining_hours", "project_id.hour_uom_id")
    def _compute_remaining_days(self):
        for record in self:
            record.remaining_days = record.project_id.convert_hours_to_days(
                record.remaining_hours
            )

    @api.depends("effective_hours", "project_id.hour_uom_id")
    def _compute_effective_days(self):
        for record in self:
            record.effective_days = record.project_id.convert_hours_to_days(
                record.effective_hours
            )
