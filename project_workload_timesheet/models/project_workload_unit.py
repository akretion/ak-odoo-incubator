# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectWorkloadUnit(models.Model):
    _inherit = "project.workload.unit"

    sheet_id = fields.Many2one("hr_timesheet.sheet")
    priority = fields.Selection(related="task_id.priority")

    def action_add(self):
        sheet_id = self.env.context.get("current_sheet_id")
        if not sheet_id:
            return
        sheet = self.env["hr_timesheet.sheet"].browse(sheet_id)
        return sheet._add_line_from_unit(self)

    def _get_timesheeting_task(self):
        # For overrides
        return self.task_id
