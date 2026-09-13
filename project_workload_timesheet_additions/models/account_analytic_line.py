# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
        "'|', "
        "'&', ('additional_task_id', '=', False), ('task_id', '=', task_id), "
        "('additional_task_id', '=', task_id)"
        "]",
    )

    def _get_available_workload_units_domain(self):
        return [
            ("week", "=", self.week),
            ("user_id", "=", self.user_id.id),
            ("project_id", "=", self.project_id.id),
            "|",
            "&",
            ("additional_task_id", "=", False),
            ("task_id", "=", self.task_id.id),
            ("additional_task_id", "=", self.task_id.id),
        ]
