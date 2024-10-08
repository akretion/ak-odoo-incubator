# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectWorkloadUnit(models.Model):
    _inherit = "project.workload.unit"
    additional_workload_id = fields.Many2one(
        "project.task.workload.addition",
        "Additional Task Workload",
        related="workload_id.additional_workload_id",
        store=True,
    )
    additional_task_id = fields.Many2one(
        "project.task",
        "Additional Task",
        related="workload_id.additional_workload_task_id",
        store=True,
    )

    def _get_timesheeting_task(self):
        # Timesheet in additional workload task
        if self.additional_workload_id:
            return self.additional_task_id
        return super()._get_timesheeting_task()
