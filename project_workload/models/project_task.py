# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

WORKLOAD_FIELDS = [
    "date_start",
    "date_end",
    "user_id",
    "planned_hours",
    "config_workload_manually",
]


class ProjectTask(models.Model):
    _inherit = "project.task"

    workload_ids = fields.One2many("project.task.workload", "task_id", "Task")
    use_workload = fields.Boolean(related="project_id.use_workload")
    config_workload_manually = fields.Boolean()

    def _prepare_workload(self):
        return {
            "task_id": self.id,
            "date_start": self.date_start,
            "date_end": self.date_end,
            "hours": self.planned_hours,
            "user_id": self.user_id.id,
        }

    def _sync_workload(self):
        for record in self:
            if not record.config_workload_manually:
                vals = self._prepare_workload()
                if record.workload_ids:
                    record.workload_ids[1:].unlink()
                    record.workload_ids.write(vals)
                else:
                    self.env["project.task.workload"].create([vals])

    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_workload()
        return records

    def write(self, vals):
        res = super().write(vals)
        if set(vals.keys()).intersection(WORKLOAD_FIELDS):
            self._sync_workload()
        return res
