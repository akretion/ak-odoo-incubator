# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
import logging
import functools
import json

_logger = logging.getLogger(__name__)

try:
    from cerberus import Validator
except ImportError:
    _logger.debug('Can not import cerberus')


def to_bool(val):
    if val == 'False':
        return False
    elif val == 'True':
        return True
    else:
        return val


def secure_params(func):
    @functools.wraps(func)
    def wrapped(self, params):
        secure_params = self._secure_params(func.__name__, params)
        return func(self, secure_params)
    return wrapped


class TaskService(models.AbstractModel):
    _name = "task.service"

    def _get_schema_for_method(self, method):
        validator_method = '_validator_%s' % method
        if not hasattr(self, validator_method):
            raise NotImplemented
        return getattr(self, validator_method)()

    def _secure_params(self, method, params):
        schema = self._get_schema_for_method(method)
        v = Validator(schema, purge_unknown=True)
        secure_params = v.normalized(params)
        if not v.errors and v.validate(secure_params):
            return secure_params
        _logger.error("BadRequest %s", v.errors)
        raise BadRequest("BadRequest %s" % v.errors)

    @secure_params
    def list(self, params):
        domain = json.loads(params['args'])
        domain += [('project_id', '=', self.project.id)]
        tasks = self.env['project.task'].search(
            domain,
            offset=params['offset'],
            limit=params['limit'],
            order=json.loads(params['order']),
            count=params['count'])
        if tasks:
            if params['count']:
                return tasks
            return tasks.ids
        return []

    @secure_params
    def get(self, params):
        tasks = self.env['project.task'].search(
            [('id', 'in', json.loads(params['ids'])),
             ('project_id', '=', self.project.id)])
        tasks = tasks.read(
            fields=json.loads(params['fields']),
            load=params['load'])
        if tasks:
            return tasks
        return []

    @secure_params
    def read_group(self, params):
        domain = json.loads(params['domain'])
        domain += [('project_id', '=', self.project.id)]
        groupby = json.loads(params['groupby'])
        fields = json.loads(params['fields'])
        tasks = self.env['project.task'].read_group(
            domain,
            fields,
            groupby,
            offset=params['offset'],
            limit=params['limit'],
            orderby=json.loads(params['orderby']),
            lazy=params['lazy'])
        # Order stages from stage id order and add fold parameter
        if 'stage_name' in groupby:
            ordered_tasks = []
            groupby = ['stage_id']
            fields.append('stage_id')
            stage_tasks = self.env['project.task'].read_group(
                domain,
                fields,
                groupby,
                offset=params['offset'],
                limit=params['limit'],
                orderby=json.loads(params['orderby']),
                lazy=params['lazy'])
            for stage_task in stage_tasks:
                for task in tasks:
                    if task['stage_name'] == stage_task['stage_id'][1]:
                        ordered_task = task
                        ordered_task['__fold'] = stage_task['__fold']
                        ordered_tasks.append(ordered_task)
            tasks = ordered_tasks
        return tasks

    @secure_params
    def create(self, params):
        params['project_id'] = self.project.id
        return self.env['project.task'].create(params).id

    @secure_params
    def update(self, params):
        tasks = self.env['project.task'].search(
            [('id', 'in', params['ids']),
             ('project_id', '=', self.project.id)])
        return tasks.write(params['vals'])

    @secure_params
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

    @secure_params
    def create_message(self, params):
        kwargs = params['kwargs']
        message = self.pool['project.task'].message_post(
            self._cr, self._uid,
            thread_id=params['thread_id'],
            body=params['body'],
            subject=params['subject'],
            type=params['type'],
            subtype=params['subtype'],
            parent_id=params['parent_id'],
            attachments=params['attachments'],
            context=self._context,
            content_subtype=params['content_subtype'],
            **kwargs)
        if message:
            return message
        return []

    # Validator
    def _validator_get(self):
        return {
            'ids': {'type': 'string'},
            'fields': {'type': 'string'},
            'load': {'type': 'string'},
            'context': {'type': 'string'},
            }

    def _validator_list(self):
        return {
            'args': {'type': 'string'},
            'offset': {'coerce': int},
            'limit': {'coerce': int, 'nullable': True, 'default': 0},
            'order': {'type': 'string'},
            'context': {'type': 'string'},
            'count': {'coerce': to_bool, 'nullable': True},
        }

    def _validator_read_group(self):
        return {
            'domain': {'type': 'string'},
            'offset': {'coerce': int},
            'limit': {'coerce': int, 'nullable': True, 'default': 0},
            'orderby': {'type': 'string'},
            'groupby': {'type': 'string'},
            'fields': {'type': 'string'},
            'context': {'type': 'string'},
            'lazy': {'coerce': to_bool, 'nullable': True},
        }

    def _validator_create(self):
        return {
            'name': {'type': 'string', 'required': True},
            'description': {'type': 'string', 'required': True},
            'external_reviewer_id': {
                'type': 'integer', 'nullable': True, 'default': 0},
            'external_user_id': {'type': 'integer', 'required':True},
            'contact_email': {'type': 'string', 'required': True},
            'contact_mobile': {'type': 'string', 'nullable': True},
            'model_reference': {'type': 'string'},
            'action_id': {'type': 'integer'},
        }

    def _validator_update(self):
        return {
            'ids': {'type': 'list', 'required': True},
            'vals': {
                'type': 'dict',
                'schema': {
                    'name': {'type': 'string'},
                    'stage_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'external_reviewer_id': {
                        'type': 'integer', 'nullable': True, 'default': 0},
                }
            }
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

    def _validator_create_message(self):
        return {
            'thread_id': {
                'anyof_type': ['integer', 'list'],
                'nullable': True,
                'default': 0},
            'body': {'type': 'string'},
            'subject': {'type': 'string', 'nullable': True},
            'type': {'type': 'string'},
            'subtype': {'type': 'string'},
            'parent_id': {'coerce': int, 'nullable': True, 'default': 0},
            'attachments': {'type': 'string', 'nullable': True},
            'content_subtype': {'type': 'string'},
            'kwargs': {
                'type': 'dict',
                'schema': {
                    'partner_ids': {'type': 'list'},
                    'attachment_ids': {'type': 'list'}
                    }
                }
            }
