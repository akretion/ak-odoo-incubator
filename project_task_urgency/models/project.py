# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    urgency_user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Urgency Contacts",
        help="Contacts to notify when a task is marked as urgent.",
    )
