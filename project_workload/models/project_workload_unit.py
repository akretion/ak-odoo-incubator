# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
        "project.project", "Project", related="workload_id.project_id"
    )

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