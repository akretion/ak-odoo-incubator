# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectWorkloadUnit(models.Model):
    _name = "project.workload.unit"
    _description = "Project Workload Unit"

    week = fields.Char()
    workload_id = fields.Many2one("project.task.workload", "Workload")
    hours = fields.Float()
    user_id = fields.Many2one(
        "res.users", "User", related="workload_id.user_id", store=True
    )
    task_id = fields.Many2one("project.task", "Task", related="workload_id.task_id")
    project_id = fields.Many2one(
        "project.project",
        "Project",
        related="workload_id.project_id",
        store=True,
    )
    done = fields.Boolean(compute="_compute_done", store=True)

    def is_done(self):
        self.ensure_one()
        return self.task_id.stage_id.is_closed

    @api.depends("task_id.stage_id.is_closed")
    def _compute_done(self):
        for record in self:
            record.done = record.is_done()

    def name_get(self):
        result = []
        for unit in self:
            result.append(
                (
                    unit.id,
                    "%s: %s" % (unit.task_id.name, unit.week),
                )
            )
        return result
