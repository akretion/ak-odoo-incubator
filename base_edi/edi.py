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

from openerp.osv.orm import BaseModel, Model
from openerp.addons.web.controllers.main import CSVExport, ExcelExport
import base64
from datetime import datetime


class EdiMixin(BaseModel):
    _name = 'edi.mixin'

    def _get_edi_attachment_vals(self, cr, uid, datas, edi_profile, 
                                 res_record, context=None):
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

    def _get_edi_file_document_vals(self, cr, uid, datas, repository,
                                    attach_id, context=None):
        tasks = [t for t in repository.task_ids if t.direction == 'out']
        task_id = tasks[0]._model._name+','+str(tasks[0].id)
        return {
            'file_type': 'export',
            'repository_id': repository.id,
            'task_id': task_id,
            'active': True,
            'direction': 'output',
            'attachment_id': attach_id,
        }        

    def create_edi_file(self, cr, uid, datas, transfer_method,
                           edi_transfer, edi_profile, res_record, context=None):
        attach_vals = self._get_edi_attachment_vals(
                cr, uid, datas, edi_profile,
                res_record,context=context)
        attach_id = self.pool['ir.attachment'].create(
                cr, uid, attach_vals, context=context)
        if transfer_method == 'repository':
            vals = self._get_edi_file_document_vals(
                cr, uid, datas, edi_transfer, attach_id, context=context)
            self.pool['file.document'].create(cr, uid, vals, context=context)
        return attach_id

    def get_edi_datas(self, cr, uid, ids, fields, fields_names,
                      file_format, context=None):
        rows = self.export_data(cr, uid, ids, fields, context=context).get('datas',[])
        if file_format == 'csv':
            datas = CSVExport().from_data(fields_names, rows)
        elif file_format == 'xls':
            datas = ExcelExport().from_data(fields_names, rows)
        else:
            raise orm.except_orm(
                _('Warning!'),
                _("The file format is not defined."))
        return datas


    def get_fields_from_export(self, cr, uid, export_id, context=None):
        export = self.pool["ir.exports"].read(cr, uid, [export_id], context=context)[0]
        export_lines = self.pool["ir.exports.line"].read(cr, uid,
            export['export_fields'], context=context)
        fields = []
        fields_name = []
        for line in export_lines:
            fields.append(line['name'])
            fields_name.append(line['display_name'] or line['name'])
        return fields, fields_name
        
        


