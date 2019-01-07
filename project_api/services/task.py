# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.base_rest.components.service import to_bool
from odoo.exceptions import UserError, MissingError, AccessError
from odoo.tools.translate import _
import json
import logging
_logger = logging.getLogger(__name__)


class ExternalTaskService(Component):
    _inherit = 'base.rest.service'
    _name = 'external.task.service'
    _collection = 'project.project'
    _usage = 'task'

    @property
    def project(self):
        return self.work.project

    def search(self, domain, offset, limit, order, count):
        domain = [('project_id', '=', self.project.id)] + domain
        tasks = self.env['project.task'].search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            count=count)
        if tasks:
            if count:
                # count will return the number of task in the tasks variable
                return tasks
            return tasks.ids
        return self.env['project.tasks'].browse([])

    def read(self, ids, fields, load):
        tasks = self.env['project.task'].search(
            [('id', 'in', ids),
             ('project_id', '=', self.project.id)])
        tasks = tasks.read(fields=fields, load=load)
        if tasks:
            for task in tasks:
                if 'message_ids' in task:
                    messages = self.env['mail.message'].search([
                        ('id', 'in', task['message_ids']),
                        '|', ('subtype_id.internal', '=', False),
                        ('subtype_id', '=', False),
                        ])
                    task['message_ids'] = [
                        'external/%s' % mid for mid in messages.ids]
            return tasks
        return self.env['project.tasks'].browse([])

    def read_group(self, domain, fields, groupby, offset=0,
            limit=None, orderby=False, lazy=True):
        domain = [('project_id', '=', self.project.id)] + domain
        tasks = self.env['project.task'].read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy)
        # Order stages from stage id order and add fold parameter
        if 'stage_name' in groupby:
            ordered_tasks = []
            groupby = ['stage_id']
            fields.append('stage_id')
            stage_tasks = self.env['project.task'].read_group(
                domain,
                fields,
                groupby,
                offset=offset,
                limit=limit,
                orderby=orderby,
                lazy=lazy)
            for stage_task in stage_tasks:
                for task in tasks:
                    if task['stage_name'] == stage_task['stage_id'][1]:
                        ordered_task = task
                        ordered_task['__fold'] = stage_task['__fold']
                        ordered_tasks.append(ordered_task)
            tasks = ordered_tasks
        return tasks

    def create(self, **params):
        partner = self._get_partner(params.pop('author'))
        params['project_id'] = self.project.id
        params['author_id'] = partner.id
        return self.env['project.task'].with_context(
            force_message_author_id=partner.id).create(params).id

    def write(self, ids, vals, author):
        partner = self._get_partner(author)
        tasks = self.env['project.task'].search(
            [('id', 'in', ids),
             ('project_id', '=', self.project.id)])
        if len(tasks) < len(ids):
            raise AccessError(
                _('You do not have the right to modify this records'))
        return tasks.with_context(
            force_message_author_id=partner.id).write(vals)

    def message_format(self, ids):
        allowed_task_ids = self.env['project.task'].search([
            ('project_id', '=', self.project.id),
            ]).ids
        messages = self.env['mail.message'].browse(ids).message_format()
        if messages:
            for message in messages:
                if message['model'] != 'project.task' or\
                        message['res_id'] not in allowed_task_ids:
                    raise AccessError(_('You can not read this message'))
                else:
                    message.update({
                        'model': 'external.task',
                        'id': 'external/%s' % message['id'],
                        })
                    author = self.env['res.partner'].browse(
                        message['author_id'][0])
                    if not author.customer_uid: # support team
                        message.pop('author_id')
                        message['support_author'] = {
                            'uid': author.id,
                            'name': author.name,
                            'update_date': author.write_date\
                                or author.create_date,
                            }
                    else:
                        message['author_id'] = (
                            author.customer_uid,
                            author.name)
            return messages
        return []

    def read_support_author(self, uid):
        """All res.user are exposed to this read only api"""
        partner = self.env['res.partner'].browse(uid)
        if partner.sudo().user_ids:
            return {
                'name': partner.name,
                'uid': uid,
                'image': partner.image,
                'update_date': partner.write_date or partner.create_date,
                }
        else:
            raise AccessError(
                _('You can not read information about this partner'))

    def get_message(self, params):
        messages = self.env['mail.message'].message_read(
            ids=json.loads(params['ids']),
            domain=json.loads(params['domain']),
            message_unload_ids=json.loads(params['message_unload_ids']),
            thread_level=params['thread_level'],
            parent_id=params['parent_id'],
            limit=params['limit'])
        if messages:
            return messages
        return []

    def _get_partner(self, data):
        customer = self.project.partner_id
        partner = self.env['res.partner'].search([
            ('parent_id', '=', customer.id),
            ('customer_uid', '=', data['uid']),
            ])
        if not partner:
            partner = self.env['res.partner'].create({
                'parent_id': customer.id,
                'image': data['image'],
                'name': data['name'],
                'customer_uid': data['uid'],
                'email': data['email'],
                'mobile': data['mobile'],
                'phone': data['phone'],
                })
        elif partner.name != data['name'] \
                or partner.image != data['image']\
                or partner.email != data['email']\
                or partner.mobile != data['mobile']:
            _logger.debug('Update partner information')
            partner.write({
                'name': data['name'],
                'image': data['image'],
                'email': data['email'],
                'mobile': data['mobile'],
                'phone': data['phone'],
                })
        return partner

    def message_post(self, _id, body, author):
        partner = self._get_partner(author)
        domain = [
            ('res_id', '=', _id),
            ('model', '=', 'project.task'),
            ]
        parent = self.env['mail.message'].search(
            domain + [('message_type', '=', 'email')],
            order="id ASC", limit=1)
        if not parent:
            parent = self.env['mail.message'].search(
                domain, order="id ASC", limit=1)
        message = self.env['mail.message'].create({
            'body': body,
            'model': 'project.task',
            'attachment_ids': [],
            'res_id': _id,
            'parent_id': parent.id,
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'author_id': partner.id,
            'message_type': 'comment',
            'partner_ids': [],
            'subject': False,
            })
        return message.id

    # Validator
    def _validator_read(self):
        return {
            'ids': {'type': 'list'},
            'fields': {'type': 'list'},
            'load': {'type': 'string'},
            'context': {'type': 'dict'},
            }

    def _validator_search(self):
        return {
            'domain': {'type': 'list'},
            'offset': {'coerce': int},
            'limit': {'coerce': int, 'nullable': True, 'default': 0},
            'order': {'type': 'string'},
            'context': {'type': 'dict'},
            'count': {'coerce': to_bool, 'nullable': True},
        }

    def _validator_read_group(self):
        return {
            'domain': {'type': 'list'},
            'offset': {'coerce': int},
            'limit': {'coerce': int, 'nullable': True, 'default': 0},
            'orderby': {'type': 'string'},
            'groupby': {'type': 'list'},
            'fields': {'type': 'list'},
            'context': {'type': 'dict'},
            'lazy': {'coerce': to_bool, 'nullable': True},
        }

    def _validator_create(self):
        return {
            'name': {'type': 'string', 'required': True},
            'description': {'type': 'string', 'required': True},
            'external_reviewer_id': {
                'type': 'integer', 'nullable': True, 'default': 0},
            'external_user_id': {'type': 'integer', 'required': True},
            'contact_email': {'type': 'string', 'required': True},
            'contact_mobile': {'type': 'string', 'nullable': True},
            'model_reference': {'type': 'string'},
            'action_id': {'type': 'integer'},
            'author': self._partner_validator()
        }

    def _validator_write(self):
        return {
            'ids': {'type': 'list'},
            'vals': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string'},
                    'stage_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'external_reviewer_id': {
                        'type': 'integer', 'nullable': True, 'default': 0},
                }
            },
            'author': self._partner_validator()
        }

    def _validator_message_format(self):
        return {
            'ids': {'type': 'list'},
            }

    def _validator_get_message(self):
        return {
            'ids': {'type': 'string'},
            'domain': {'type': 'string'},
            'message_unload_ids': {'type': 'string'},
            'thread_level': {'coerce': int, 'nullable': True, 'default': 0},
            'context': {'type': 'string'},
            'parent_id': {'coerce': int, 'nullable': True, 'default': 0},
            'limit': {'coerce': int, 'nullable': True, 'default': 0},
            }

    def _validator_message_post(self):
        return {
            '_id': {'type': 'integer'},
            'body': {'type': 'string'},
            'author': self._partner_validator()
            }

    def _partner_validator(self):
        return {
            'type': 'dict',
            'schema': {
                'name': {'type': 'string'},
                'uid': {'type': 'integer'},
                'image': {'type': 'string'},
                'email': {'type': 'string'},
                'mobile': {'type': 'string'},
                'phone': {'type': 'string'},
                }
            }
    def _validator_read_support_author(self):
        return {
            'uid': {'type': 'integer'},
            }
