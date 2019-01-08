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
import urllib


ISSUE_DESCRIPTION = u"""Ce qui ne va pas:
---------------------------


Voilà comment cela devrait fonctionner:
-----------------------------------------------------------
"""


class ExternalTask(models.Model):
    _name = 'external.task'

    def _get_select_project(self):
        return self._call_odoo('project_list', {})

    name = fields.Char('Name')
    stage_name = fields.Char('Stage')
    description = fields.Text('Description', default=ISSUE_DESCRIPTION)
    message_ids = fields.One2many(
        comodel_name='external.message', inverse_name='res_id')
    create_date = fields.Datetime('Create Date', readonly=True)
    author_id = fields.Many2one(
        'res.partner', string='Author', readonly=True)
    assignee_id = fields.Many2one(
        'res.partner', string='Assignee name', readonly=True)
    origin_name = fields.Char()
    origin_url = fields.Char()
    origin_db = fields.Char()
    origin_model = fields.Char()
    project_id = fields.Selection(
        selection=_get_select_project,
        string='Project')

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
        url = '%s/project-api/task/%s' % (url_key['url'], method)
        headers = {'API_KEY': url_key['api_key']}
        res = requests.post(url, headers=headers, json=params)
        return res.json()

    def _get_support_partner_vals(self, support_uid):
        vals = self._call_odoo('read_support_author', {'uid': support_uid})
        return {
            'name': vals['name'],
            'support_last_update_date': vals['update_date'],
            'image': vals['image'],
            'support_uid': vals['uid'],
            'parent_id': self.env.ref('project_api_client.support_team').id,
            }

    def _get_support_partner(self, data):
        """ This method will return the partner info in the client database
        If the partner is missing it will be created
        If the partner information are obsolet their will be updated"""
        partner = self.env['res.partner'].search([
            ('support_uid', '=', data['uid'])
            ])
        if not partner:
            vals = self._get_support_partner_vals(data['uid'])
            partner = self.env['res.partner'].create(vals)
        elif partner.support_last_update_date < data['update_date']:
            vals = self._get_support_partner_vals(data['uid'])
            partner.write(vals)
        return partner

    def _map_partner_data_to_id(self, data):
        if not data:
            return False
        elif data['type'] == 'customer':
            return data['vals']
        else:
            partner = self._get_support_partner(data)
            return (partner.id, partner.name)

    @api.model
    def create(self, vals):
        vals = self._add_missing_default_values(vals)
        vals['author'] = self._get_author_info()
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
        if not isinstance(self.ids, list):
            multi = False
        tasks = self._call_odoo('read', {
            'ids': self.ids,
            'fields': fields,
            'load': load
            })
        for task in tasks:
            if 'author_id' in fields:
                task['author_id'] = self._map_partner_data_to_id(
                    task['author_id'])
            if 'assignee_id' in fields:
                task['assignee_id'] = self._map_partner_data_to_id(
                    task['assignee_id'])
        return tasks

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
            'email': partner.email or '',
            'mobile': partner.mobile or '',
            'phone': partner.phone or '',
            }

    @api.multi
    def message_post(self, body='', **kwargs):
        mid = self._call_odoo('message_post', {
            '_id': self.id,
            'body': body,
            'author': self._get_author_info(),
            })
        return 'external/%s' % mid

    @api.model
    def message_get(self, external_ids):
        messages = self._call_odoo('message_format', {'ids': external_ids})
        for message in messages:
            if 'author_id' in message:
                message['author_id'] = self._map_partner_data_to_id(
                    message['author_id'])
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
        if view_type == 'search':
            doc = etree.XML(res['arch'])
            node = doc.xpath("//search")[0]
            for project_id, project_name in self._get_select_project():
                elem = etree.Element(
                    'filter',
                    string=project_name,
                    domain="[('project_id', '=', %s)]" % project_id)
                node.append(elem)
            res['arch'] = etree.tostring(doc, pretty_print=True)
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


class ExternalMessage(models.Model):
    _name = 'external.message'

    res_id = fields.Many2one(comodel_name='external.task')


class MailMessage(models.Model):
    _inherit = 'mail.message'

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

    def _set_origin_in_context(self, action):
        context = {'default_origin_db': self._cr.dbname}
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        params = {}
        action_id = self._context.get('params', {}).get('action')
        _id = self._context.get('active_id')
        model = self._context.get('active_model')
        if _id and model:
            record = self.env[model].browse(_id)
            context['default_origin_name'] = record.display_name
            context['default_origin_model'] = model
        if action_id and _id:
            path = urllib.urlencode({
                'view_type': 'form',
                'action_id': action_id,
                'id': _id,
                })
            context['default_origin_url'] = '%s#%s' %(base_url, path)
        action['context'] = context

    def read(self, fields=None, load='_classic_read'):
        res = super(IrActionActWindows, self).read(fields=fields, load=load)
        if not self.env.context.get('install_mode'):
            task_action_id = self.env.ref(
                'project_api_client.task_from_elsewhere')
            if self == task_action_id:
                self._set_origin_in_context(res[0])
        return res
