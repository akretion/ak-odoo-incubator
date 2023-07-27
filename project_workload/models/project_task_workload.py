# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectTaskWorkload(models.Model):
    _name = "project.task.workload"
    _description = "Project Task Workload"

    task_id = fields.Many2one("project.task", "Task", required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    user_id = fields.Many2one("res.users", "User", required=True)
    hours = fields.Float(required=True)
