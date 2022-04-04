# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProjectEstimateStep(models.Model):
    _name = 'project.estimate.step'
    _description = 'Project Estimate Step'
    _order = "days, name"

    name = fields.Char(required=True)
    days = fields.Float(required=True)
