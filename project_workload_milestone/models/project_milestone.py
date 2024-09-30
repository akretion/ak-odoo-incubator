# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    start_date = fields.Date(
        string="Start Date",
        help="The date when the Milestone should start.",
        compute="_compute_milestone_start_date",
        store=True,
        readonly=False,
    )

    @api.constrains("start_date", "deadline")
    def _check_start_date(self):
        for milestone in self:
            if (
                milestone.deadline
                and milestone.start_date
                and milestone.deadline < milestone.start_date
            ):
                raise ValidationError(
                    _("The end date cannot be earlier than the start date.")
                )

    @api.depends("deadline", "project_id")
    def _compute_milestone_start_date(self):
        for record in self:
            if record.start_date:
                continue
            if not record.deadline:
                record.start_date = False
                continue

            # Use a simple algorithm to find the start date
            # Find previous milestone
            previous_milestones = self.search(
                [
                    ("project_id", "=", record.project_id.id),
                    ("deadline", "<", record.deadline),
                ],
                order="deadline desc",
                limit=1,
            )
            # The start date will be the end date of the previous milestone
            if previous_milestones.deadline:
                record.start_date = previous_milestones.deadline + timedelta(days=1)
