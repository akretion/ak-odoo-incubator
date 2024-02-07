# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    workload_ids = fields.One2many(
        "project.task.workload",
        "task_id",
        "Task",
        compute="_compute_workload_ids",
        store=True,
    )
    workload_unit_ids = fields.One2many(
        "project.workload.unit",
        compute="_compute_workload_unit_ids",
        string="Workload Units",
    )
    use_workload = fields.Boolean(related="project_id.use_workload")
    config_workload_manually = fields.Boolean()

    @api.depends(
        "date_start",
        "date_end",
        "planned_hours",
        "user_id",
        "config_workload_manually",
        "use_workload",
    )
    def _compute_workload_ids(self):
        for record in self:
            record.workload_ids = self.env["project.task.workload"].search(
                [("task_id", "=", record.id)]
            )
            if not record.use_workload:
                continue

            # Handle only automatic config in planned task
            if record.config_workload_manually or not (
                record.date_start and record.date_end and record.planned_hours
            ):
                continue

            vals = record._prepare_workload()
            # Handle only one workload in automatic
            if record.workload_ids:
                # Remove other workloads and update the first workload values
                record.workload_ids = [
                    (1, record.workload_ids[0].id, vals),
                    *[(2, workload_id.id) for workload_id in record.workload_ids[1:]],
                ]
            else:
                # Create the workload
                record.workload_ids = [(0, 0, vals)]

    def _prepare_workload(self):
        return {
            "date_start": self.date_start,
            "date_end": self.date_end,
            "hours": self.planned_hours,
            "user_id": self.user_id.id,
        }

    @api.depends("workload_ids.unit_ids")
    def _compute_workload_unit_ids(self):
        # related doesn't retrieve all the data so we need to compute it
        for record in self:
            record.workload_unit_ids = record.workload_ids.unit_ids
