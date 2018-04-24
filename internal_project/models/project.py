# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015-TODAY Akretion (http://www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    api_key = fields.Char('Project Api Key')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    stage_name = fields.Char(
        'Stage', compute='_compute_stage_name', inverse='_inverse_stage_name',
        store=True)
    contact_mobile = fields.Char(string='Mobile')
    contact_email = fields.Char(string='Email')
    external_reviewer_id = fields.Integer(
        string='Reviewer')
    external_user_id = fields.Integer(
        string='Created by')
    assignee_name = fields.Char(
        'Assignee name', related='user_id.name', store=True)

    @api.depends('stage_id')
    def _compute_stage_name(self):
        for task in self:
            task.stage_name = task.stage_id.name

    def _inverse_stage_name(self):
        for task in self:
            stages = self.env['project.task.type'].search([
                ('project_ids', 'in', [task.project_id.id]),
                ('name', '=', self.stage_name)])
            if stages:
                task.stage_id = stages[0].id
