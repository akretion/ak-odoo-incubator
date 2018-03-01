# coding: utf-8
# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


INV_FIELDS = {
    'date': {},
    'company_id': {},
    'location_id': {},
}


def sheet_name(name):
    for char in ['[', ']', ':', '*', '?', '/', '\\']:
        name = name.replace(char, ' ')
    return name[:31]


class InventoryValuation(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, odoo_objects):
        self._set_format_definition(workbook)
        for inv in odoo_objects:
            sheet = workbook.add_worksheet(sheet_name(inv.name))
            bold = workbook.add_format({'bold': True})
            # header
            y = 0
            sheet.write(0, 4, "INVENTAIRE VALORISE", bold)
            for key in INV_FIELDS.keys():
                y += 1
                myfield = inv[key]
                if inv._fields[key].type == 'many2one' and hasattr(
                        inv[key], 'name'):
                    myfield = inv[key]['name']
                sheet.write(y, 0, inv._fields[key].string, bold)
                sheet.write(y, 1, myfield, bold)
            #

    def _set_format_definition(self, workbook):
        base_format = {
            'font_size': 10,
            'text_wrap': True}
        self.format = workbook.add_format(base_format)
        self.emphasis = workbook.add_format(base_format)
        self.emphasis.set_bold()
        self.emphasis.set_top(3)
        self.separator_format = workbook.add_format(base_format)
        self.separator_format.set_top(3)
        self.format.set_text_wrap()
        self.date_format = workbook.add_format({
            'font_size': 10,
            'text_wrap': True,
            'num_format': 'dd/mm/yy',
        })
        self.separator_date_format = workbook.add_format({
            'font_size': 10,
            'text_wrap': True,
            'num_format': 'dd/mm/yy', 'top': 3
        })
        self.header_format = workbook.add_format({
            'bg_color': 'silver',
            'font_size': 10,
            'align': 'vcenter',
            'bold': True})
        self.total_format = workbook.add_format({
            'num_format': '# ### ##0.0',
            'bg_color': 'orange',
            'align': 'center',
            'font_size': 10,
            'bold': True})


InventoryValuation('report.stock.inventory.xlsx', 'stock.inventory')
