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
        "planned_date_start",
        "planned_date_end",
        "planned_hours",
        "user_ids",
        "config_workload_manually",
        "use_workload",
    )
    def _compute_workload_ids(self):
        for record in self:
            if not record.use_workload:
                continue

            # Handle only automatic config in planned task
            if record.config_workload_manually or not (
                record.planned_date_start
                and record.planned_date_end
                and record.planned_hours
            ):
                continue
            record.workload_ids = record._get_workload_sync()

    def _prepare_workload(self, user, **extra):
        return {
            "date_start": self.planned_date_start,
            "date_end": self.planned_date_end,
            "hours": self.planned_hours,
            "user_id": user.id,
            **extra,
        }

    def _get_workload_sync(self):
        self.ensure_one()
        return [
            *[(0, 0, vals) for vals in self._get_new_workloads()],
            *[
                (1, workload.id, vals)
                for workload, vals in self._get_updated_workloads()
            ],
            *[(2, workload.id) for workload in self._get_obsolete_workloads()],
        ]

    def _get_main_workloads(self):
        return self.workload_ids

    def _get_new_workloads(self):
        self.ensure_one()
        workloads = self._get_main_workloads()
        # Handle only one workload per user in automatic
        new_vals = []
        for user in self.user_ids:
            user_workload = workloads.filtered(lambda w: w.user_id == user)
            if not user_workload:
                new_vals.append(self._prepare_workload(user))

        return new_vals

    def _get_updated_workloads(self):
        self.ensure_one()
        workloads = self._get_main_workloads()
        vals = []
        # Update the users workload values
        for workload in workloads:
            if workload.user_id in self.user_ids:
                vals.append((workload, self._prepare_workload(workload.user_id)))
        return vals

    def _get_obsolete_workloads(self):
        self.ensure_one()
        workloads = self._get_main_workloads()
        # Remove other workloads, dedup for users?
        return workloads.filtered(lambda w: w.user_id not in self.user_ids)

    @api.depends("workload_ids.unit_ids")
    def _compute_workload_unit_ids(self):
        # related doesn't retrieve all the data so we need to compute it
        for record in self:
            record.workload_unit_ids = record.workload_ids.unit_ids
