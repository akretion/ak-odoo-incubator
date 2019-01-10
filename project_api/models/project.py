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

from odoo import fields, api, models, tools


class ProjectProject(models.Model):
    _inherit='project.project'

    customer_project_name = fields.Char(
        help='Name that will appear on customer support menu',
        index=True)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    stage_name = fields.Char(
        'Stage', compute='_compute_stage_name', inverse='_inverse_stage_name',
        store=True)
    author_id = fields.Many2one(
        'res.partner',
        default=lambda self: self.env.user.partner_id.id,
        string='Create By')
    partner_id = fields.Many2one(
        related='project_id.partner_id',
        readonly=True)
    user_id = fields.Many2one(default=False)
    assignee_id = fields.Many2one('res.partner', related='user_id.partner_id')
    origin_name = fields.Char()
    origin_url = fields.Char()
    origin_db = fields.Char()
    origin_model = fields.Char()

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

    @api.model
    def create(self, vals):
        vals.pop('partner_id', None) # readonly
        return super(ProjectTask, self).create(vals)

    def write(self, vals):
        vals.pop('partner_id', None) # readonly
        return super(ProjectTask, self).write(vals)

    def message_auto_subscribe(self, updated_fields, values=None):
        super(ProjectTask, self).message_auto_subscribe(
            updated_fields, values=values)
        if values.get('author_id'):
            self.message_subscribe([values['author_id']], force=False)
        return True

    def message_get_suggested_recipients(self):
        # we do not need this feature
        return {}

    @api.model
    def message_new(self, msg, custom_values=None):
        partner_email = tools.email_split(msg['from'])[0]
        # Automatically create a partner
        if not msg.get('author_id'):
            alias = tools.email_split(msg['to'])[0].split('@')[0]
            project = self.env['project.project'].search([
                ('alias_name', '=', alias),
                ])
            partner = self.env['res.partner'].create({
                'parent_id': project.partner_id.id,
                'name': partner_email.split('@')[0],
                'email': partner_email,
                })
            msg['author_id'] = partner.id
        if custom_values is None:
            custom_values = {}
        custom_values.update({
            'description': msg['body'],
            'author_id': msg['author_id'],
            })
        return super(ProjectTask, self).message_new(
            msg, custom_values=custom_values)
