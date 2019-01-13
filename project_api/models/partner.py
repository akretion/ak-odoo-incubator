# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_uid = fields.Integer()
    project_auth_api_key_id = fields.Many2one(
        'auth.api.key',
        string="Project API KEY")
    help_desk_project_id = fields.Many2one(
        'project.project',
        string="Help Desk Project")
