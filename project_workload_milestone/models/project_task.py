# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    date_start = fields.Datetime(
        compute="_compute_date_start_end",
        store=True,
        readonly=False,
    )
    date_end = fields.Datetime(
        compute="_compute_date_start_end",
        store=True,
        readonly=False,
    )

    @api.depends("milestone_id.start_date", "milestone_id.target_date")
    def _compute_date_start_end(self):
        for record in self:
            record.date_end = record.milestone_id.target_date
            record.date_start = record.milestone_id.start_date
