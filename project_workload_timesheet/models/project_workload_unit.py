# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectWorkloadUnit(models.Model):
    _inherit = "project.workload.unit"

    timesheet_ids = fields.One2many(
        "account.analytic.line",
        "workload_unit_id",
        "Timesheets",
        help="The timesheets (normally one) in which the workload is timesheeted",
    )
    priority = fields.Selection(related="task_id.priority")

    timesheeted_hours = fields.Float(
        "Timesheeted Hours",
        compute="_compute_timesheeted_hours",
        help="The hours timesheeted on this workload",
    )
    remaining_hours = fields.Float(
        "Remaining Hours",
        compute="_compute_remaining_hours",
        help="The remaining hours to timesheet on this workload (can be negative)",
    )
    progress = fields.Float(
        "Progress",
        compute="_compute_progress",
        help="The progress of the task",
    )
    done = fields.Boolean(
        "Done",
    )
    task_stage_id = fields.Many2one(
        related="task_id.stage_id", string="Task Stage", readonly=False
    )

    @api.depends("timesheet_ids.unit_amount")
    def _compute_timesheeted_hours(self):
        for record in self:
            record.timesheeted_hours = sum(record.timesheet_ids.mapped("unit_amount"))

    @api.depends("hours", "timesheeted_hours")
    def _compute_progress(self):
        for record in self:
            if record.hours:
                record.progress = 100 * record.timesheeted_hours / record.hours
            else:
                record.progress = 0

    @api.depends("hours", "timesheeted_hours", "done")
    def _compute_remaining_hours(self):
        for record in self:
            if record.done:
                record.remaining_hours = 0
            else:
                record.remaining_hours = record.hours - record.timesheeted_hours

    def action_add_to_timesheet(self):
        sheet_id = self.env.context.get("current_sheet_id")
        if not sheet_id:
            return
        sheet = self.env["hr_timesheet.sheet"].browse(sheet_id)
        return sheet._add_line_from_unit(self)

    def action_timesheet_time(self):
        sheet_id = self.env.context.get("current_sheet_id")
        if not sheet_id:
            return
        sheet = self.env["hr_timesheet.sheet"].browse(sheet_id)
        if not sheet or not sheet.current:
            return
        time = self.env.context.get("time", 0) / 60

        # Add only on lines without names
        timesheet = self.timesheet_ids.filtered(
            lambda t: t.date == fields.Date.today() and t.name == "/"
        )
        if len(timesheet) > 1:
            timesheet = timesheet[0]
        if not timesheet:
            timesheet = sheet._add_line_from_unit(self)
        timesheet.unit_amount += time
        return True

    def action_timesheet_done(self):
        self.done = True

    def _get_timesheeting_task(self):
        # For overrides
        return self.task_id
