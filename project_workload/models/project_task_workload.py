# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

WEEK_FORMAT = "%Y-%W"


def week_name(value):
    if value:
        return value.strftime(WEEK_FORMAT)
    return None


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
    unit_ids = fields.One2many(
        "project.workload.unit",
        "workload_id",
        "Units",
        compute="_compute_unit_ids",
        store=True,
    )

    @api.constrains("date_start", "date_end")
    def _check_end_date(self):
        for task in self:
            if task.date_end < task.date_start:
                raise ValidationError(
                    _("The end date cannot be earlier than the start date.")
                )

    @api.depends("date_start", "date_end", "hours")
    def _compute_unit_ids(self):
        for record in self:
            record.unit_ids = self.env["project.workload.unit"].search(
                [
                    ("workload_id", "=", record.id),
                ]
            )
            # We need to have the data to compute the unit (this happens at create)
            if not record.date_start or not record.date_end or not record.hours:
                continue
            record._check_end_date()
            hours_per_week = record._get_hours_per_week()
            unit_per_week = {wl.week: wl for wl in record.unit_ids}
            commands = []
            for week, hours in hours_per_week.items():
                unit = unit_per_week.get(week)
                if unit:
                    if unit.hours != hours:
                        # Update unit
                        commands.append((1, unit.id, {"hours": hours}))
                else:
                    # Create unit
                    commands.append(
                        (
                            0,
                            0,
                            {
                                "hours": hours,
                                "week": week,
                            },
                        )
                    )
            for week, unit in unit_per_week.items():
                if week not in hours_per_week:
                    # Remove not in week anymore unit
                    commands.append((2, unit.id))

            record.unit_ids = commands

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

    def name_get(self):
        result = []
        for task in self:
            if not task.date_start or not task.date_end:
                continue
            week_start = week_name(task.date_start)
            week_end = week_name(task.date_end - timedelta(days=7))
            name = f"{_('Load')} {week_start}"
            if week_end > week_start:
                name += f" - {week_end}"
            name += f": {task.hours}h"
            result.append((task.id, name))
        return result
