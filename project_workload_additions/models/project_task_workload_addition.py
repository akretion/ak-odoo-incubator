# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProjectWorkloadAddition(models.Model):
    _name = "project.task.workload.addition"
    _description = "Project Task Workload Addition"

    project_id = fields.Many2one("project.project", string="Project", required=True)
    type = fields.Many2one(
        "project.task.workload.addition.type", string="Addition Type", required=True
    )
    percentage = fields.Float(
        required=True,
        string="Added Percentage",
    )
    user_id = fields.Many2one("res.users", string="User", required=True)
    task_id = fields.Many2one("project.task", string="Task", required=True)

    @api.onchange("type")
    def _onchange_type(self):
        self.percentage = self.type.default_percentage

    def _compute_hours_from_task(self, task):
        self.ensure_one()
        return task.planned_hours * (self.percentage / 100)

    def name_get(self):
        result = []
        for record in self:
            result.append(
                (
                    record.id,
                    _(
                        "%s additional workload (%d%%)"
                        % (record.task_id.name, record.percentage)
                    ),
                )
            )
        return result
