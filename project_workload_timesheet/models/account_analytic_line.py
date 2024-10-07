# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.project_workload.models.project_task_workload import week_name


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    workload_unit_id = fields.Many2one(
        comodel_name="project.workload.unit",
        string="Workload Unit",
        readonly=False,
        compute="_compute_workload_unit_id",
        store=True,
        domain="["
        "('week', '=', week), "
        "('user_id', '=', user_id), "
        "('project_id', '=', project_id), "
        "('task_id', '=', task_id)"
        "]",
    )

    week = fields.Char(
        compute="_compute_week",
        help="Week number of the year",
    )

    @api.depends("date")
    def _compute_week(self):
        for record in self:
            record.week = week_name(record.date)

    @api.depends("task_id", "date", "user_id")
    def _compute_workload_unit_id(self):
        for record in self:
            if not record.project_id or not record.task_id:
                record.workload_unit_id = False
                continue
            available_workload_units = self.env["project.workload.unit"].search(
                record._get_available_workload_units_domain()
            )
            if (
                not record.workload_unit_id
                or record.workload_unit_id not in available_workload_units
            ):
                record.workload_unit_id = (
                    available_workload_units[0]
                    if len(available_workload_units) > 0
                    else False
                )

    def _get_available_workload_units_domain(self):
        return [
            ("project_id", "=", self.project_id.id),
            ("task_id", "=", self.task_id.id),
            ("week", "=", self.week),
            ("user_id", "=", self.user_id.id),
        ]
