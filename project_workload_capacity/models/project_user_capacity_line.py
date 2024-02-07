# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectUserCapacityLine(models.Model):
    _name = "project.user.capacity.line"
    _description = "Project User Capacity Line"

    capacity_id = fields.Many2one("project.user.capacity")
    date_start = fields.Date(required=True, default=fields.Date.today())
    date_end = fields.Date()
    hours = fields.Float()
    modulo = fields.Integer(default=1, string="Repeat", help="Repeat every X week")
