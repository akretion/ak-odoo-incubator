# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# © 2015 OpenERP SA (http://odoo.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.web.controllers.main import ExcelExport
import datetime
import re
import xlwt
from cStringIO import StringIO


class ExcelExport(ExcelExport):
    _color = ['gray25', 'white']

    def from_data(self, fields, rows):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        idx_id = None
        for i, fieldname in enumerate(fields):
            if fieldname == 'id':
                idx_id = i
            worksheet.write(0, i, fieldname)
            worksheet.col(i).width = 8000  # around 220 pixels
        style = []
        for color in self._color:
            str_style = (
                'pattern: pattern solid;'
                'pattern: fore_colour %s;'
                'align: wrap yes'
                % color)
            style.append({
                'base': xlwt.easyxf(str_style),
                'date': xlwt.easyxf(str_style, num_format_str='YYYY-MM-DD'),
                'datetime': xlwt.easyxf(
                    str_style, num_format_str='YYYY-MM-DD HH:mm:SS'),
                })
        color_idx = 0
        for row_index, row in enumerate(rows):
            if idx_id is not None and row[idx_id]:
                color_idx = (color_idx + 1) % len(self._color)
            for cell_index, cell_value in enumerate(row):
                cell_style = style[color_idx]['base']
                if isinstance(cell_value, basestring):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value, datetime.datetime):
                    cell_style = style[color_idx]['datetime']
                elif isinstance(cell_value, datetime.date):
                    cell_style = style[color_idx]['date']
                worksheet.write(
                    row_index + 1, cell_index, cell_value, cell_style)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data
