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

from odoo import fields, api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    auth_api_key_id = fields.Many2one('auth.api.key')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    stage_name = fields.Char(
        'Stage', compute='_compute_stage_name', inverse='_inverse_stage_name',
        store=True)
    author_id = fields.Many2one('res.partner', string='Create By')
    assignee_id = fields.Many2one('res.partner', related='user_id.partner_id')

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

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        if self._context.get('force_message_author_id'):
            kwargs['author_id'] = self._context['force_message_author_id']
        return super(ProjectTask, self).message_post(
            body=body, subject=subject, message_type=message_type,
            subtype=subtype, parent_id=parent_id, attachments=attachments,
            content_subtype=content_subtype, **kwargs)
