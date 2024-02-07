# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectWorkloadAdditionType(models.Model):
    _name = "project.task.workload.addition.type"
    _description = "Project Task Workload Addition Type"

    name = fields.Char(required=True)
    description = fields.Text()
    default_percentage = fields.Float(required=True, default=10)
    active = fields.Boolean(default=True)
