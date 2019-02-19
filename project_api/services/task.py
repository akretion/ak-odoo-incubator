# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8106

from odoo.addons.component.core import Component
from odoo.addons.base_rest.components.service import to_bool
from odoo.exceptions import AccessError
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
    def partner(self):
        return self.work.partner

    def _map_partner_read_to_data(self, partner_read):
        if not partner_read or not partner_read[0]:
            # partner_read[0] can have the value 0 when their is not
            # partner linked to the message
            return False
        else:
            partner = self.env['res.partner'].browse(partner_read[0])
            if partner.customer_uid:
                return {
                    'type': 'customer',
                    'vals': (partner.customer_uid, partner.name),
                    }
            elif partner.user_ids:
                return {
                    'type': 'support',
                    'uid': partner.id,
                    'update_date': partner.write_date or partner.create_date,
                    }
            else:
                return {
                    'type': 'anonymous',
                    'vals': (0, partner.name),
                    }

    def search(self, domain, offset, limit, order, count):
        domain = [('project_id.partner_id', '=', self.partner.id)] + domain
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
        return []

    def read(self, ids, fields, load):
        tasks = self.env['project.task'].search(
            [('id', 'in', ids),
             ('project_id.partner_id', '=', self.partner.id)])
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
                if 'author_id' in task:
                    task['author_id'] = self._map_partner_read_to_data(
                        task['author_id'])
                if 'assignee_id' in task:
                    task['assignee_id'] = self._map_partner_read_to_data(
                        task['assignee_id'])
            return tasks
        return []

    def _get_all_project_ids_from_domain(self, domain):
        # Note we apply a filter on a project we will always
        # show all stage of this project
        # this is not a perfect solution aand will not work with
        # advanced filtering on client side
        all_project_ids = self.env['project.project'].search([
            ('partner_id', '=', self.partner.id),
            ]).ids
        project_ids = []
        for elem in domain:
            if len(elem) == 3\
                    and elem[0] == 'project_id' and elem[1] == '=':
                if elem[2] in all_project_ids:
                    project_ids.append(elem[2])
        return project_ids

    def read_group(self, domain, fields, groupby, offset=0,
                   limit=None, orderby=False, lazy=True):
        domain = [('project_id.partner_id', '=', self.partner.id)] + domain
        task_obj = self.env['project.task']
        if 'stage_name' in groupby[0]:
            groupby[0] = 'stage_id'
            fields[fields.index('stage_name')] = 'stage_id'
            project_ids = self._get_all_project_ids_from_domain(domain)
            task_obj = task_obj.with_context(
                stage_from_project_ids=project_ids)
        groups = task_obj.read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy)
        if groupby[0] == 'stage_id':
            for group in groups:
                group['stage_name'] = group.pop('stage_id')[1]
                group['stage_name_count'] = group.pop('stage_id_count')
        return groups

    def create(self, **params):
        partner = self._get_partner(params.pop('author'))
        params['project_id'] = self.partner.help_desk_project_id.id
        params['author_id'] = partner.id
        task = self.env['project.task'].with_context(
            force_message_author_id=partner.id).create(params)
        return task.id

    def write(self, ids, vals, author, assignee=None):
        author = self._get_partner(author)
        tasks = self.env['project.task'].search(
            [('id', 'in', ids),
             ('project_id.partner_id', '=', self.partner.id)])
        if len(tasks) < len(ids):
            raise AccessError(
                _('You do not have the right to modify this records'))
        if assignee:
            vals['assignee_customer_id'] = self._get_partner(assignee).id
        return tasks.with_context(
            force_message_author_id=author.id).write(vals)

    def message_format(self, ids):
        allowed_task_ids = self.env['project.task'].search([
            ('project_id.partner_id', '=', self.partner.id),
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
                    message['author_id'] = self._map_partner_read_to_data(
                        message['author_id'])
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
        domain = [('parent_id', '=', self.partner.id)]
        if data.get('email'):
            domain += [
                '|',
                ('customer_uid', '=', data['uid']),
                ('email', '=', data['email']),
                ]
        else:
            domain += [('customer_uid', '=', data['uid'])]
        partner = self.env['res.partner'].search(domain)
        if not partner:
            partner = self.env['res.partner'].create({
                'parent_id': self.partner.id,
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
                'customer_uid': data['uid'],
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

    def project_list(self):
        helpdesk = self.partner.help_desk_project_id
        projects = self.env['project.project'].search([
            ('partner_id', '=', self.partner.id),
            ('id', '!=', helpdesk.id)])
        return [(helpdesk.id, helpdesk.customer_project_name)]\
            + [(p.id, p.customer_project_name) for p in projects]

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
            'origin_model': {'type': 'string'},
            'origin_url': {'type': 'string'},
            'origin_db': {'type': 'string'},
            'origin_name': {'type': 'string'},
            'action_id': {'type': 'integer'},
            'project_id': {'type': 'integer'},
            'author': self._partner_validator(),
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
                    'project_id': {'type': 'integer'},
                }
            },
            'author': self._partner_validator(),
            'assignee': self._partner_validator()
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
                'image': {'type': 'string', 'nullable': True},
                'email': {'type': 'string'},
                'mobile': {'type': 'string'},
                'phone': {'type': 'string'},
                }
            }

    def _validator_read_support_author(self):
        return {
            'uid': {'type': 'integer'},
            }

    def _validator_project_list(self):
        return {}
