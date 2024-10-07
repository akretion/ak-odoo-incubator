# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _prepare_task_dates_vals_from_milestone(self, vals):
        # If we create a task with a milestone or affect it after,
        # we set the task dates to the milestone dates

        if "milestone_id" in vals:
            milestone = self.env["project.milestone"].browse(vals["milestone_id"])
            if milestone:
                vals["planned_date_end"] = milestone.deadline
                vals["planned_date_start"] = milestone.start_date
        return vals

    @api.model
    def create(self, vals):
        return super().create(self._prepare_task_dates_vals_from_milestone(vals))

    def write(self, vals):
        return super().write(self._prepare_task_dates_vals_from_milestone(vals))
