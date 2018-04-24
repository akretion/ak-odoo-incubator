# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval
from lxml import etree
import requests
import json


ISSUE_DESCRIPTION = u"""Ce qui ne va pas:
---------------------------


Voilà comment cela devrait fonctionner:
-----------------------------------------------------------
"""


class ExternalTask(models.Model):
    _name = 'external.task'

    @api.model
    def _get_default_external_user(self):
        return self.env.user

    @api.model
    def _get_origin(self):
        if self.model_reference:
            rec_name = self.model_reference._rec_name
            if rec_name:
                self.task_origin = self.model_reference.display_name

    @api.model
    def _authorised_models(self):
        """ Inherit this method to add more models depending of your
            modules dependencies
        """
        models = self.env['ir.model'].search(
            [('model', '!=', 'external.task')])
        return [(x.model, x.name) for x in models]

    action_id = fields.Many2one(
        'ir.actions.act_window', string="Action",
        help="Action called to go to the original window.")
    model_reference = fields.Reference(
        selection='_authorised_models')
    task_origin = fields.Char(compute='_get_origin')
    name = fields.Char('Name')
    stage_name = fields.Char('Stage')
    description = fields.Text('Description', default=ISSUE_DESCRIPTION)
    message_ids = fields.One2many(
        comodel_name='external.message', inverse_name='res_id')
    create_date = fields.Datetime('Create Date', readonly=True)
    external_user_id = fields.Many2one(
        comodel_name='res.users', string='Created by',
        default=_get_default_external_user)
    external_reviewer_id = fields.Many2one(
        comodel_name='res.users', string='Reviewer')
    assignee_name = fields.Char('Assignee name')

    def get_url_key(self):
        keychain = self.env['keychain.account']
        if self.env.user.has_group('base.group_user'):
            retrieve = keychain.suspend_security().retrieve
        else:
            retrieve = keychain.retrieve

        account = retrieve(
            [['namespace', '=', 'external_project']])[0]
        return {
            'url': account.login,
            'api_key': account.get_password()
        }

    @api.model
    def _call_odoo(self, method, params):
        url_key = self.get_url_key()
        url = '%s/externaltask/task' % url_key['url']
        if method == 'get':
            kwargs = {'params': params}
        else:
            kwargs = {'json': params}
        headers = {'API_KEY': url_key['api_key']}
        res = getattr(requests, method)(url, headers=headers, **kwargs)
        return res.json()

    @api.model
    def create(self, vals):
        method = 'post'
        vals = self._add_missing_default_values(vals)
        if vals.get('external_user_id', False):
            user = self.env['res.users'].browse(vals['external_user_id'])
            vals.update({
                'contact_email': user.email,
                'contact_mobile': user.mobile or '',
            })
        task_id = self._call_odoo(method, vals)
        return self.browse(task_id)

    @api.multi
    def write(self, vals):
        method = 'put'
        payload = {
            'ids': self.ids,
            'vals': vals
        }
        return self._call_odoo(method, payload)

    @api.multi
    def unlink(self):
        return True

    @api.model
    def copy(self, default):
        return self

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        method = 'get'
        payload = {
            'method': 'read',
            'ids': json.dumps(self.ids),
            'fields': json.dumps(fields),
            'context': json.dumps(self.context),
            'load': load
        }
        return self._call_odoo(method, payload)

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        method = 'get'
        payload = {
            'method': 'search',
            'args': json.dumps(args),
            'offset': offset,
            'limit': limit,
            'order': json.dumps(order),
            'context': json.dumps(self.env.context),
            'count': count
        }
        return self._call_odoo(method, payload)

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0,
            limit=None, orderby=False, lazy=True):
        import pdb; pdb.set_trace()
        method = 'get'
        payload = {
            'method': 'read_group',
            'domain': json.dumps(domain),
            'fields': json.dumps(fields),
            'groupby': json.dumps(groupby),
            'offset': offset,
            'limit': limit or None,
            'orderby': json.dumps(orderby),
            'context': json.dumps(self.env.context),
            'lazy': lazy
        }
        return self._call_odoo(method, payload)

    @api.multi
    def message_get_suggested_recipients(self):
        result = dict((task.id, []) for task in self)
        return result

    @api.cr_uid_ids_context
    def message_post(
            self, thread_id, body='', subject=None,
            type='notification', subtype=None, parent_id=False,
            attachments=None, context=None, content_subtype='html', **kwargs):
        method = 'post'
        payload = {
            'thread_id': thread_id or 0,
            'body': body,
            'subject': subject or '',
            'type': type,
            'subtype': subtype,
            'parent_id': parent_id or 0,
            'attachments': attachments,
            'content_subtype': content_subtype,
            'kwargs': kwargs
        }
        return self.pool['mail.message']._call_odoo(method, payload)

    @api.model
    def fields_view_get(
            self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(ExternalTask, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='message_ids']"):
                options = json.loads(node.get('options', '{}'))
                options.update({'display_log_button': False})
                node.set('options', json.dumps(options))
            res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def default_get(self, fields):
        vals = super(ExternalTask, self).default_get(fields)
        if 'from_model' in self._context and 'from_id' in self._context:
            vals['model_reference'] = '%s,%s' % (self._context['from_model'],
                                                 self._context['from_id'])
        if 'from_action' in self._context:
            vals['action_id'] = self._context['from_action']
        return vals

    @api.multi
    def goto_document(self):
        self.ensure_one()
        if self.model_reference:
            action = {
                'name': 'Task to original document',
                'res_model': self.model_reference._model._name,
                'res_id': self.model_reference.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_mode': 'form',
            }
            if self.action_id:
                action['id'] = self.action_id.id
                action['action_id'] = self.action_id.id
                view = [x.view_id for x in self.action_id.view_ids
                        if x.view_mode == 'form']
                if view:
                    view_ref = self.env['ir.model.data'].search(
                        [('res_id', '=', view[0].id),
                         ('model', '=', 'ir.ui.view')])
                    if view_ref:
                        action['context'] = {'form_view_ref': '%s.%s' % (
                            view_ref.module, view_ref.name)}
            return action
        raise UserError(_(
            "Field 'Task Origin' is not set.\n"
            "Impossible to go to the original document."))


class ExternalMessage(models.Model):
    _name = 'external.message'

    res_id = fields.Many2one(comodel_name='external.task')


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _call_odoo(self, method, params):
        url_key = self.env['external.task'].get_url_key()
        url = '%s/externaltask/message' % url_key['url']
        if method == 'get':
            kwargs = {'params': params}
        else:
            kwargs = {'json': params}
        headers = {'API_KEY': url_key['api_key']}
        res = getattr(requests, method)(url, headers=headers, **kwargs)
        return res.json()

    @api.cr_uid_context
    def message_read(
            self, domain=None, message_unload_ids=None,
            thread_level=0, context=None, parent_id=False, limit=None):
        if context.get('default_model', '') == 'external.task':
            method = 'get'
            payload = {
                'ids': json.dumps(self.ids),
                'domain': json.dumps(domain),
                'message_unload_ids': json.dumps(message_unload_ids),
                'thread_level': thread_level or None,
                'context': json.dumps(context),
                'parent_id': parent_id,
                'limit': limit,
            }
            return self._call_odoo(method, payload)
        return super(MailMessage, self).message_read(
            domain=domain,
            message_unload_ids=message_unload_ids, thread_level=thread_level,
            context=context, parent_id=parent_id, limit=limit)


class IrActionActWindows(models.Model):
    _inherit = 'ir.actions.act_window'

    # @api.multi
    # def read(self, fields=None, load='_classic_read'):
    #     if self.context.get('install_mode'):
    #         return super(IrActionActWindows, self).read(
    #             fields=fields, load=load)

    #     def update_context(action):
    #         action['context'] = safe_eval(action.get('context', '{}'))
    #         action['context'].update({
    #             'from_model': self.env.selfcontext.get('active_model'),
    #             'from_id': self.env.context.get('active_id'),
    #         })
    #         if 'params' in self.env.context and 'action':
    #             action['context'].update({
    #                 'from_action': self.env.context['params'].get('action')})
    #         if 'params' in self.env.context and 'action':
    #             action['context'].update({
    #                 'from_action': self.env.context['params'].get('action')})
    #     res = super(IrActionActWindows, self).read(fields=fields, load=load)
    #     action_id = self

    #     task_action_id = self.env.ref('external_project.task_from_elsewhere')
    #     if action_id == task_action_id:
    #         if isinstance(res, list):
    #             for elem in res:
    #                 update_context(elem)
    #         else:
    #             update_context(res)
    #     return res
