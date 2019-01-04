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

class RemoteObject(models.AbstractModel):
    _name = 'remote.object'

    def get_url_key(self):
        keychain = self.env['keychain.account']
        if self.env.user.has_group('base.group_user'):
            retrieve = keychain.suspend_security().retrieve
        else:
            retrieve = keychain.retrieve
        account = retrieve(
            [['namespace', '=', 'support']])[0]
        return {
            'url': account.get_data()['url'],
            'api_key': account._get_password()
        }

    @api.model
    def _call_odoo(self, method, params):
        url_key = self.get_url_key()
        url = '%s/project-api/%s/%s' % (url_key['url'], self._path, method)
        headers = {'API_KEY': url_key['api_key']}
        res = requests.post(url, headers=headers, json=params)
        return res.json()


class ExternalTask(models.Model):
    _inherit = 'remote.object'
    _name = 'external.task'
    _path = 'task'

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

    @api.model
    def create(self, vals):
        vals = self._add_missing_default_values(vals)
        vals['author'] = self._get_author_info()
        if vals.get('external_user_id', False):
            user = self.env['res.users'].browse(vals['external_user_id'])
            vals.update({
                'contact_email': user.email,
                'contact_mobile': user.mobile or '',
            })
        if not vals.get('model_reference', False):
            vals['model_reference'] = ''
        task_id = self._call_odoo('create', vals)
        return self.browse(task_id)

    @api.multi
    def write(self, vals):
        return self._call_odoo('write', {
            'ids': self.ids,
            'vals': vals,
            'author': self._get_author_info(),
            })

    @api.multi
    def unlink(self):
        return True

    @api.model
    def copy(self, default):
        return self

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        return self._call_odoo('read', {
            'ids': self.ids,
            'fields': fields,
            'load': load
            })

    @api.model
    def search(self, domain, offset=0, limit=0, order=None, count=False):
        result = self._call_odoo('search', {
            'domain': domain,
            'offset': offset,
            'limit': limit,
            'order': order or '',
            'count': count
            })
        if count:
            return result
        else:
            return self.browse(result)

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0,
            limit=None, orderby=False, lazy=True):
        return self._call_odoo('read_group', {
            'domain': domain,
            'fields': fields,
            'groupby': groupby or [],
            'offset': offset,
            'limit': limit,
            'orderby': orderby or '',
            'lazy': lazy
            })

    @api.multi
    def message_get_suggested_recipients(self):
        result = dict((task.id, []) for task in self)
        return result

    def _get_author_info(self):
        partner = self.env.user.partner_id
        return {
            'uid': partner.id,
            'name': partner.name,
            'image': partner.image_small,
            }

    @api.multi
    def message_post(self, body='', **kwargs):
        mid = self._call_odoo('message_post', {
            '_id': self.id,
            'body': body,
            'author': self._get_author_info(),
            })
        return 'external/%s' % mid

    def _get_support_author_vals(self, support_uid):
        vals = self._call_odoo('read_support_author', {'uid': support_uid})
        return {
            'name': vals['name'],
            'support_last_update_date': vals['update_date'],
            'image': vals['image'],
            'support_uid': vals['uid'],
            'parent_id': self.env.ref('project_api_client.support_team').id,
            }

    def _get_support_author(self, data):
        """ This method will return the partner info in the client database
        If the partner is missing it will be created
        If the partner information are obsolet their will be updated"""
        partner = self.env['res.partner'].search([
            ('support_uid', '=', data['uid'])
            ])
        if not partner:
            vals = self._get_support_author_vals(data['uid'])
            partner = self.env['res.partner'].create(vals)
        elif partner.support_last_update_date < data['update_date']:
            vals = self._get_support_author_data(data['uid'])
            partner.write(vals)
        return (partner.id, partner.name)

    @api.model
    def message_get(self, external_ids):
        messages = self._call_odoo('message_format', {'ids': external_ids})
        for message in messages:
            if 'support_author' in message:
                message['author_id'] = self._get_support_author(
                    message.pop('support_author'))
        return messages

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
    _inherit = ['mail.message', 'remote.object']
    _name = 'mail.message'
    _path = 'task'

    @api.multi
    def message_format(self):
        ids = self.ids
        if isinstance(ids[0], (str, unicode)) and 'external' in ids[0]:
            external_ids = [int(mid.replace('external/', '')) for mid in ids]
            return self.env['external.task'].message_get(external_ids)
        else:
            return super(MailMessage, self).message_format()

    @api.multi
    def set_message_done(self):
        ids = self.ids
        for _id in self.ids:
            if isinstance(_id, (str, unicode)) and 'external' in _id:
                return True
        else:
            return super(MailMessage, self).set_message_done()



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
