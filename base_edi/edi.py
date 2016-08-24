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
import base64
from datetime import datetime


class EdiMixin(models.Model):
    _name = 'edi.mixin'

    @api.model
    def _get_edi_attachment_vals(self, datas, edi_profile, res_record):
        today = datetime.now().strftime('%Y-%m-%d')
        name = '%s_%s.%s' % (today, edi_profile.name, edi_profile.file_format)

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
    def _get_edi_metadata_attachment_vals(self, datas, location,
                                          attach_id):
        tasks = [t for t in location.task_ids if t.method_type == 'export']
        task = tasks[0]
        return {
            'file_type': 'export_external_location',
            'task_id': task.id,
            'active': True,
            'attachment_id': attach_id,
        }        

    @api.model
    def create_edi_file(self, datas, transfer_method,
                           edi_transfer, edi_profile, res_record):
        attach_vals = self._get_edi_attachment_vals(
                datas, edi_profile, res_record)
        attach = self.env['ir.attachment'].create(
                attach_vals)
        if transfer_method == 'external_location':
            vals = self._get_edi_metadata_attachment_vals(
                datas, edi_transfer, attach.id)
            self.env['ir.attachment.metadata'].create(vals)
        return attach

    @api.multi
    def get_edi_datas(self, fields, fields_names,
                      file_format):
        rows = self.export_data(fields).get('datas',[])
        if file_format == 'csv':
            datas = CSVExport().from_data(fields_names, rows)
        elif file_format == 'xls':
            datas = ExcelExport().from_data(fields_names, rows)
        else:
            raise exceptions.UserError(
                _("The file format is not defined."))
        return datas


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
        
        


