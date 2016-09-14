# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Akretion (<http://www.akretion.com>).
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

from openerp import models, fields


class IrExports(models.Model):
    _inherit = "ir.exports"

    export_database_ext_id = fields.Boolean()
    filename = fields.Char(
        help='Exported File will be renamed to this name '
             'Name can use mako template where obj depend on the export '
             'it could be a purchase order, a sale order...'
             ' Example : ${obj.name}-${obj.create_date}.csv')


class IrExportsLine(models.Model):
    _inherit = "ir.exports.line"

    display_name = fields.Char()
