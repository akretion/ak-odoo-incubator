# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

WEEK_FORMAT = "%Y-%W"


def week_name(value):
    if value:
        return value.strftime(WEEK_FORMAT)
    return None


week_merge_re = re.compile((r"(\d{4})-(\d{2}) - (\1)-(\d{2})"))


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
        string="Units",
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
        for load in self:
            if not load.date_start or not load.date_end:
                continue
            week_start = week_name(load.date_start)
            end = load.date_end
            if load.date_start.weekday() > load.date_end.weekday():
                end -= timedelta(days=7)
            week_end = week_name(end)
            name = f"{load.task_id.name}: {week_start}"
            if week_end > week_start:
                name += f" - {week_end}"
                name = week_merge_re.sub(r"\1-\2->\4", name)
            result.append((load.id, name))
        return result
