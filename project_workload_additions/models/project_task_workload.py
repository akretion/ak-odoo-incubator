# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectTaskWorkload(models.Model):
    _inherit = "project.task.workload"

    additional_workload_id = fields.Many2one(
        "project.task.workload.addition", string="Additional Workload Reference"
    )
