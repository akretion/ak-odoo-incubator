# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    allowed_gitlab_id_projects = fields.Char(
        string="Allowed GitLab Project IDs",
        help="Comma-separated list of GitLab project IDs that are allowed to "
        "be linked to this Odoo project. "
        "If empty, no Merge Requests will be linked.",
    )
