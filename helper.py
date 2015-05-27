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


class ProxyActionHelper(orm.AbstractModel):
    _name="proxy.action.helper"

    def _build_print_action(self, cr, uid, data,
                            printer_name='laser',
                            raw=False,
                            copies=1,
                            host='http://localhost',
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
        (result, format) = service.create(cr, uid, ids, {
            'model': model,
            }, context)
        return base64.b64encode(result)

    def get_print_action(self, cr, uid, report_name,
                     model, object_ids, **kwargs):
        data = self._get_report(
            cr, uid, report_name, model,
            object_ids, context=kwargs.get('context'))
        return self._build_print_action(cr, uid, data, **kwargs)

    def return_action(self, todo):
        return {
            'type': 'ir.actions.proxy',
            'action_list': todo,
            }
