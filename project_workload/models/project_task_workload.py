# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import timedelta

from odoo import fields, models

from .project_capacity_unit import week_name


class ProjectTaskWorkload(models.Model):
    _name = "project.task.workload"
    _description = "Project Task Workload"

    project_id = fields.Many2one(
        "project.project", "Project", related="task_id.project_id", store=True
    )
    task_id = fields.Many2one("project.task", "Task", required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    user_id = fields.Many2one("res.users", "User", required=True)
    hours = fields.Float(required=True)
    unit_ids = fields.One2many("project.workload.unit", "workload_id", "Units")

    def _get_hours_per_week(self):
        weeks = set()
        date = self.date_start
        while True:
            weeks.add(week_name(date))
            date += timedelta(days=7)
            if date > self.date_end:
                break
        # For now a simple stupid split is done by week
        # we do not care of the exact start / stop date
        hours = self.hours / len(weeks)
        return {week: hours for week in weeks}

    def _sync_workload_unit(self):
        vals_list = []
        for record in self:
            hours_per_week = self._get_hours_per_week()
            unit_per_week = {wl.week: wl for wl in self.unit_ids}
            for week, hours in hours_per_week.items():
                unit = unit_per_week.get(week)
                if unit:
                    if unit.hours != hours:
                        unit.hours = hours
                else:
                    vals_list.append(
                        {
                            "workload_id": record.id,
                            "hours": hours,
                            "week": week,
                        }
                    )
            for week, unit in unit_per_week.items():
                if week not in hours_per_week:
                    unit.unlink()
        self.env["project.workload.unit"].create(vals_list)

    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_workload_unit()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._sync_workload_unit()
        return res
