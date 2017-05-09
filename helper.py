# coding: utf-8
# Copyright 2014 Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2017 Sylvain CALADOR <sylvain.calador@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
import base64


class ProxyActionHelper(models.AbstractModel):
    _name = "proxy.action.helper"
    _description = "Forward HTTP actions to front-end proxy"

    @api.model
    def get_print_data_action(
            self, data,
            printer_name=None,
            raw=False,
            to_encode64=False,
            copies=1,
            host='https://localhost'):
        """ Prepare a PyWebdriver.print action """
        if to_encode64:
            data = base64.b64encode(data)
        kwargs = {'options': {}}
        if copies > 1:
            kwargs['options']['copies'] = copies
        if raw:
            kwargs['options']['raw'] = True
        return {
            'url': '%s/cups/printData' % host,
            'params': {
                'args': [printer_name, data],
                'kwargs': kwargs,
                }
            }

    @api.model
    def get_print_xml_receipt_action(
            self, receipt,
            host='https://localhost'):
        """ Prepare a PyWebdriver.print action """

        return {
            'url': '%s/hw_proxy/print_xml_receipt' % host,
            'params' : {
                'args': [receipt],
                }
            }

    def send_proxy(self, todo):
        """ @param todo: list of requests
                         (printings, webservices)
        """
        return {
            'type': 'ir.actions.act_proxy',
            'action_list': todo,
            }
