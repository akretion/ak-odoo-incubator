# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv.orm import Model
from openerp.osv import fields

class IrExports(Model):
    _inherit = "ir.exports"

    _columns = {
        'export_database_id': fields.boolean('Export Database ID'),
    }

    def add_remove_id_field_line(self, cr, uid, ids, action, context=None):
        line_obj = self.pool['ir.exports.line']
        for id in ids:
            id_line_ids = line_obj.search(
                cr, uid, [('name', '=', '.id')], context=context)
            if not id_line_ids and action == 'add':
                vals = {
                    'export_id': id,
                    'name': '.id',
                }
                line_obj.create(cr, uid, vals, context=context)
            elif id_line_ids and action== 'remove':
                line_obj.unlink(cr, uid, id_line_ids, context=context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        res = super(IrExports, self).write(
            cr, uid, ids,  vals, context=context)
        if 'export_database_id' in vals:
            if vals['export_database_id']:
                self.add_remove_id_field_line(
                    cr, uid, ids, 'add', context=context)
            else:
                self.add_remove_id_field_line(
                    cr, uid, ids, 'remove', context=context)
        return res

class IrExportsLine(Model):
    _inherit = "ir.exports.line"
    _order = 'sequence asc'

    _columns = {
        'sequence': fields.integer('Sequence'),
    }
