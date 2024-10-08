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
        string="Workload Units",
        compute="_compute_workload_unit_ids",
        readonly=False,
    )

    next_week_load = fields.Float(
        "Next Week Load",
        compute="_compute_next_week_load",
        help="The workload of the next week",
    )
    next_week_units_count = fields.Integer(
        "Next Week Units Count",
        compute="_compute_next_week_load",
        help="The number of workload units of the next week",
    )

    current = fields.Boolean(
        "Current",
        compute="_compute_current",
        help="Is this the current timesheet",
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
                .sorted(
                    lambda p: (
                        p.done,  # Put done tasks at the end
                        -int(p.priority or 0),  # Sort by priority
                        p.remaining_hours,  # Sort by remaining hours
                        -p.id,  # Stabilize sort
                    )
                )
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
            record.next_week_units_count = len(next_week_units)
            record.next_week_load = sum(next_week_units.mapped("hours"))

    @api.depends("date_start", "date_end")
    def _compute_current(self):
        for record in self:
            record.current = record.date_start <= fields.Date.today() <= record.date_end

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
            task = unit._get_timesheeting_task()
            if self.current:
                values["date"] = fields.Date.today()

            values["unit_amount"] = 0
            values["project_id"] = task.project_id.id
            values["task_id"] = task.id
            values["workload_unit_id"] = unit.id
            return self.env["account.analytic.line"]._sheet_create(values)

    @api.model
    def _prepare_new_line(self, line):
        # We need to check if the new line is similar to a worload unit
        # If it is, we need to link it to the workload unit
        vals = super()._prepare_new_line(line)
        # Yeah, using the same function for 2 different things leads to this :/
        if line._name != "hr_timesheet.sheet.new.analytic.line":
            return vals
        timesheets = line.sheet_id.timesheet_ids
        similar_timesheets = timesheets.filtered(
            lambda t: t.project_id == line.project_id and t.task_id == line.task_id
        )
        if not similar_timesheets:
            return vals

        similar_workload_units = similar_timesheets.mapped("workload_unit_id")
        vals["workload_unit_id"] = (
            similar_workload_units.ids[0] if similar_workload_units else False
        )
        return vals

    def action_timesheet_done(self):
        self.ensure_one()
        super().action_timesheet_done()

        next_week = week_name(self.date_start + timedelta(days=7))
        next_week_units = self.env["project.workload.unit"].search(
            [
                ("week", "=", next_week),
                ("user_id", "=", self.user_id.id),
            ],
        )

        unfinished_units = self.workload_unit_ids.filtered(lambda u: not u.done)
        for unit in unfinished_units:
            next_week_unit = next_week_units.filtered(
                lambda u: u.project_id == unit.project_id
                and u.task_id == unit.task_id
                and u.workload_id == unit.workload_id
            )

            # But we report the remaining hours to the next week
            # We also report if the remaining hours are negative
            # It will decrease the next week workload
            # But we don't create a unit in this case
            if not next_week_unit and unit.remaining_hours > 0:
                # And we create a new unit if it does not exist
                # Even if the unit could be after end_date for now
                next_week_unit = self.env["project.workload.unit"].create(
                    {
                        "task_id": unit.task_id.id,
                        "workload_id": unit.workload_id.id,
                        "week": next_week,
                        "hours": unit.remaining_hours,
                    }
                )
            else:
                next_week_unit.hours += unit.remaining_hours

            # The unit are now done so the unit hours are the timesheeted hours
            unit.hours = unit.timesheeted_hours
