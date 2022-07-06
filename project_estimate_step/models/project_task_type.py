# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    to_estimate = fields.Boolean()
    current_sprint = fields.Boolean()
