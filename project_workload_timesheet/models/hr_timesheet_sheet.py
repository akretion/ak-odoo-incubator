# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models

from odoo.addons.project_workload.models.project_task_workload import week_name


class Sheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    workload_unit_ids = fields.One2many(
        "project.workload.unit",
        "sheet_id",
        string="Workload Units",
        compute="_compute_workload_unit_ids",
    )

    next_week_load = fields.Float(
        "Next Week Load",
        compute="_compute_next_week_load",
        help="The workload of the next week",
    )

    @api.depends("date_start", "date_end", "user_id")
    def _compute_workload_unit_ids(self):
        for record in self:
            week = week_name(self.date_start)  # Use only start date for now
            record.workload_unit_ids = (
                self.env["project.workload.unit"]
                .search(
                    [
                        ("week", "=", week),
                        ("user_id", "=", record.user_id.id),
                    ],
                )
                .sorted(lambda p: -int(p.priority or 0))  # Hum
            )

    @api.depends("date_start", "date_end", "user_id")
    def _compute_next_week_load(self):
        for record in self:
            next_week = week_name(self.date_start + timedelta(days=7))
            next_week_units = self.env["project.workload.unit"].search(
                [
                    ("week", "=", next_week),
                    ("user_id", "=", record.user_id.id),
                ],
            )

            record.next_week_load = sum(next_week_units.mapped("hours"))

    def button_open_next_week(self):
        self.ensure_one()
        next_week = self.date_start + timedelta(days=7)
        date_start = self._get_period_start(self.env.user.company_id, next_week)
        date_end = self._get_period_end(self.env.user.company_id, next_week)
        next_week_sheet = self.env["hr_timesheet.sheet"].search(
            [
                ("date_start", "=", date_start),
                ("date_end", "=", date_end),
                ("user_id", "=", self.user_id.id),
            ],
            limit=1,
        )
        view = {
            "name": "Next Week",
            "type": "ir.actions.act_window",
            "res_model": "hr_timesheet.sheet",
            "view_id": self.env.ref(
                "project_workload_timesheet.hr_timesheet_sheet_form_my"
            ).id,
            "view_mode": "form",
            "context": {
                "default_date_start": date_start,
                "default_date_end": date_end,
                "default_user_id": self.user_id.id,
            },
            "target": "current",
        }
        if next_week_sheet:
            view["res_id"] = next_week_sheet.id

        return view

    def _add_line_from_unit(self, unit):
        if self.state not in ["new", "draft"]:
            return
        values = self._prepare_empty_analytic_line()
        new_line_unique_id = self._get_new_line_unique_id()
        existing_unique_ids = list(
            {frozenset(line.get_unique_id().items()) for line in self.line_ids}
        )
        if existing_unique_ids:
            self.delete_empty_lines(False)
        if frozenset(new_line_unique_id.items()) not in existing_unique_ids:
            # TODO MAKE this configurable
            DAILY_HOURS = 8
            task = unit._get_timesheeting_task()

            if task.date_start and task.date_end:
                task_start = task.date_start.date()
                task_end = task.date_end.date()

                today = fields.Date.today()
                # If this is the current week
                if self.date_start <= today <= self.date_end:
                    # Take the closest day to today
                    values["date"] = max(min(today, task_end), task_start)
                else:
                    # If start date is in week, take it
                    if self.date_start <= task_start <= self.date_end:
                        values["date"] = task_start

            values["unit_amount"] = min(DAILY_HOURS, unit.hours)
            values["project_id"] = task.project_id.id
            values["task_id"] = task.id
            self.timesheet_ids |= self.env["account.analytic.line"]._sheet_create(
                values
            )
        return True
