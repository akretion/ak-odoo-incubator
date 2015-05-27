# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


from openerp.osv import fields, orm
from openerp import netsvc
import base64


class ProxyActionHelper(orm.AbstractModel):
    _name="proxy.action.helper"

    def get_print_data_action(
            self, cr, uid, data,
            printer_name='laser',
            raw=False,
            copies=1,
            host='https://localhost',
            context=None):
        kwargs = {'options':{}}
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

    def _get_report(self, cr, uid, report_name, model, object_ids,
                    context=None):
        service = netsvc.LocalService(report_name)
        (result, format) = service.create(cr, uid, object_ids, {
            'model': model,
            }, context)
        return base64.b64encode(result)

    def get_print_report_action(self, cr, uid, report_name,
                     model, object_ids, **kwargs):
        data = self._get_report(
            cr, uid, report_name, model,
            object_ids, context=kwargs.get('context'))
        return self.get_print_data_action(cr, uid, data, **kwargs)

    def return_action(self, todo):
        return {
            'type': 'ir.actions.act_proxy',
            'action_list': todo,
            }
