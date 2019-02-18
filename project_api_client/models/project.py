# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8106

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from lxml import etree
from odoo.tools.safe_eval import safe_eval
import requests
import urllib
import logging
_logger = logging.getLogger(__name__)


ISSUE_DESCRIPTION = _(u"""What is not working:
</br>
</br>
</br>
</br>
How this should work:
""")


class ExternalTask(models.Model):
    _name = 'external.task'

    def _get_select_project(self):
        # solve issue during installation and test
        # If we have an uid it's a real call from webclient
        if self._context.get('uid'):
            return self._call_odoo('project_list', {})
        else:
            return []

    name = fields.Char('Name')
    stage_name = fields.Char('Stage')
    description = fields.Html('Description', default=ISSUE_DESCRIPTION)
    message_ids = fields.One2many(
        comodel_name='external.message', inverse_name='res_id')
    create_date = fields.Datetime('Create Date', readonly=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High')
    ], default='1')
    date_deadline = fields.Datetime('Date deadline', readonly=True)
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
    color = fields.Integer(string='Color Index')

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
        headers = {'API-KEY': url_key['api_key']}
        user_error_message =\
            _('There is an issue with support. Please send an email')
        try:
            res = requests.post(url, headers=headers, json=params)
        except Exception as e:
            _logger.error('Error when calling odoo %s', e)
            raise UserError(user_error_message)
        data = res.json()
        if isinstance(data, dict) and data.get('code', 0) >= 400:
            _logger.error(
                'Error Support API : %s : %s',
                data.get('name'),
                data.get('description'))
            raise UserError(user_error_message)
        return data

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
            ('support_uid', '=', str(data['uid']))
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
        elif data['type'] in ('customer', 'anonymous'):
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
        params = {
            'ids': self.ids,
            'vals': vals,
            'author': self._get_author_info(),
            }
        if vals.get('assignee_id'):
            partner = self.env['res.partner'].browse(vals['assignee_id'])
            if not partner.user_ids:
                raise UserError(_('You can only assign ticket to your users'))
            else:
                params['assignee'] = self._get_partner_info(partner)
        return self._call_odoo('write', params)

    @api.multi
    def unlink(self):
        return True

    @api.multi
    def copy(self, default):
        return self

    @api.multi
    def read(self, fields=None, load='_classic_read'):
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
        return self._get_partner_info(self.env.user.partner_id)

    def _get_partner_info(self, partner):
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
                options = safe_eval(node.get('options', '{}'))
                options.update({'display_log_button': False})
                node.set('options', repr(options))
            res['arch'] = etree.tostring(doc)
        if view_type == 'search':
            doc = etree.XML(res['arch'])
            node = doc.xpath("//search")[0]
            for project_id, project_name in self._get_select_project():
                elem = etree.Element(
                    'filter',
                    string=project_name,
                    name='project_%s' % project_id,
                    domain="[('project_id', '=', %s)]" % project_id)
                node.append(elem)
            node = doc.xpath("//filter[@name='my_task']")[0]
            node.attrib['domain'] = "[('assignee_id.customer_uid', '=', %s)]"\
                % self.env.user.partner_id.id
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
        if ids and isinstance(ids[0], (str, unicode)) and 'external' in ids[0]:
            external_ids = [int(mid.replace('external/', '')) for mid in ids]
            return self.env['external.task'].message_get(external_ids)
        else:
            return super(MailMessage, self).message_format()

    @api.multi
    def set_message_done(self):
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
            context['default_origin_url'] = '%s#%s' % (base_url, path)
        action['context'] = context

    def _set_default_project(self, action):
        # we add a try/except to avoid raising a pop-up want odoo server
        # is down
        try:
            projects = self.env['external.task']._get_select_project()
            if projects:
                key = 'search_default_project_%s' % projects[0][0]
                action['context'] = {key: 1}
        except Exception:
            _logger.warning('Fail to add the default project')

    @api.model
    def _update_action(self, action):
        account = self.env['keychain.account'].sudo().retrieve(
            [('namespace', '=', 'support')])
        if not account:
            return
        action_support = self.env.ref(
            'project_api_client.action_helpdesk', False)
        if action_support and action['id'] == action_support.id:
            self._set_origin_in_context(action)
        action_external_task = self.env.ref(
            'project_api_client.action_view_external_task', False)
        if action_external_task and action['id'] == action_external_task.id:
            self._set_default_project(action)

    def read(self, fields=None, load='_classic_read'):
        res = super(IrActionActWindows, self).read(fields=fields, load=load)
        for action in res:
            self._update_action(action)
        return res
