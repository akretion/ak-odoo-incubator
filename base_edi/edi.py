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

from openerp import models, api, fields, exceptions
from openerp.addons.web.controllers.main import CSVExport, ExcelExport
from openerp import tools
import base64
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        variable_start_string="${",
        variable_end_string="}",
        line_statement_prefix="%",
        trim_blocks=True,               # do not output newline after blocks
    )
    mako_template_env.globals.update({
        'str': str,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': reduce,
        'map': map,
        'round': round,
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class EdiProfile(models.AbstractModel):
    _name = "edi.profile"

    name = fields.Char(required=True)
    export_id = fields.Many2one(
        'ir.exports',
        'Export',)
    file_format = fields.Selection(
            selection=[('csv', 'CSV'), ('xls', 'Excel')],
            required=True,
            string='File Format')
    filename = fields.Char(
        help='Exported File will be renamed to this name '
             'Name can use mako template where obj depend on the export '
             'it could be a purchase order, a sale order...'
             ' Example : ${obj.name}-${obj.create_date}.csv')


class EdiMixin(models.Model):
    _name = 'edi.mixin'

    @api.model
    def _get_edi_file_name(self, edi_profile, res_record):
        today = datetime.now().strftime('%Y-%m-%d')
        filename = '%s_%s.%s' % (today, edi_profile.name,
                                 edi_profile.file_format)
        return filename

    @api.model
    def _get_edi_attachment_vals(self, datas, edi_profile, res_record):
        if edi_profile.filename:
            name = self._template_render(edi_profile.filename, res_record)
        else:
            name = self._get_edi_file_name(edi_profile, res_record)

        model = res_record and res_record._name or False
        res_id = res_record and res_record.id or False
        return {
            'name': name,
            'datas': base64.encodestring(datas),
            'datas_fname': name,
            'res_model': model,
            'res_id': res_id,
        }

    @api.model
    def create_edi_file(self, datas,
                           edi_profile, res_record):
        attach_vals = self._get_edi_attachment_vals(
                datas, edi_profile, res_record)
        attach = self.env['ir.attachment'].create(
                attach_vals)
        return attach

    @api.multi
    def _get_additional_rows(self, rows, fields_names):
        "Surcharge if you have to perform some action before creating the "
        " definitive file "
        return rows, fields_names

    @api.multi
    def _get_values_from_ir_exports(self, export):
        fields, fields_names = self.get_fields_from_export(
            export.id)
        rows = self.export_data(fields).get('datas',[])
        rows, fields_names = self._get_additional_rows(rows, fields_names)
        return rows, fields_names

    @api.multi
    def get_edi_datas(self, edi_profile):
        file_format = edi_profile.file_format
        data = False
        if file_format in ("csv", "xls"):
            rows, fields_names = self._get_values_from_ir_exports(edi_profile.export_id)
            if file_format == 'csv':
                data = CSVExport().from_data(fields_names, rows)
            elif file_format == 'xls':
                data = ExcelExport().from_data(fields_names, rows)
        return data

    @api.model
    def get_fields_from_export(self, export_id):
        export = self.env["ir.exports"].browse(export_id)
        fields = []
        fields_name = []
        if export.export_database_ext_id:
            fields.append('id')
            fields_name.append('Ext Id')
        for line in export.export_fields:
            fields.append(line.name)
            fields_name.append(line.display_name or line.name)
        return fields, fields_name
        
    @api.model
    def _template_render(self, template, record):
        try:
            template = mako_template_env.from_string(tools.ustr(template))
        except Exception:
            _logger.exception("Failed to load template %r", template)
        variables = {'obj': record}
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.exception(
                "Failed to render template %r using values %r" %
                (template, variables))
            render_result = u""
        if render_result == u"False":
            render_result = u""
        return render_result
