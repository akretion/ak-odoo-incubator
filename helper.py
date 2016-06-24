# coding: utf-8
# Copyright 2014 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
import base64


class ProxyActionHelper(models.Model):
    _name = "proxy.action.helper"
    _description = "Use this object to collect action to send to servers"

    @api.model
    def get_print_data_action(
            self, data,
            printer_name=None,
            raw=False,
            to_encode64=False,
            copies=1,
            host='https://localhost'):
        """ Method to send send print action tu cups
            In Odoo to populate pdf data use:
            self.env['report'].get_pdf(object_ids, report_name)"""
        if to_encode64:
            data = base64.b64encode(data)
        kwargs = {'options': {}}
        if copies > 1:
            kwargs['options']['copie'] = copies
        if raw:
            kwargs['options']['raw'] = True
        return {
            'url': '%s/cups/printData' % host,
            'params': {
                'args': [printer_name, data],
                'kwargs': kwargs,
                }
            }

    def send_proxy(self, todo):
        """ @param todo: list of requests to send to servers
                         (printings, webservices)
        """
        return {
            'type': 'ir.actions.act_proxy',
            'action_list': todo,
            }
