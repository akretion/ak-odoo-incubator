# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    gitlab_merge_request_ids = fields.Many2many(
        comodel_name="gitlab.merge.request",
        string="Related Gitlab MRs",
        help="Gitlab Merge Requests associated with this task.",
        # readonly=True,
    )
