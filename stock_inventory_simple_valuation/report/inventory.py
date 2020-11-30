# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _


INV_FIELDS = ["date", "company_id", "location_id"]

LINE_FIELDS = [
    "product_id",
    "product_uom_id",
    "location_id",
    "product_qty",
    "manual_product_cost",
    "total_value",
    "origin_record_name",
    "explanation",
]
LINE_PARAMS = {
    "product_id": {"size": 40, "string": _("Product")},
    "product_uom_id": {"size": 7, "string": _("Units")},
    "location_id": {"size": 20, "string": _("Location")},
    "product_qty": {"size": 5, "string": _("Quantity")},
    "manual_product_cost": {"size": 7, "string": _("Manual value")},
    "value": {"size": 7, "string": _("Value")},
    "explanation": {"size": 20, "string": _("Explanation")},
}


def sheet_name(inventory):
    for char in ["[", "]", ":", "*", "?", "/", "\\"]:
        inventory.name = inventory.name.replace(char, " ")
    name = "{} {}".format(inventory.id, inventory.name)
    return name[:31]


class SimpleInventoryValuation(models.AbstractModel):
    _name = "report.stock_inventory_simple_valuation.valuation_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, odoo_objects):
        self._set_format_definition(workbook)
        for inv in odoo_objects:
            sheet = workbook.add_worksheet(sheet_name(inv))
            bold = workbook.add_format({"bold": True})
            # inventory header
            y = 0
            sheet.write(0, 2, _("INVENTORY VALUATION"), bold)
            for key in INV_FIELDS:
                y += 1
                myfield = inv[key]
                if inv._fields[key].type == "many2one" and hasattr(
                    inv[key], "name"
                ):
                    myfield = inv[key]["name"]
                sheet.write(y, 0, inv._fields[key].string, bold)
                sheet.write(y, 1, myfield, bold)
            # inventory lines header
            y = len(INV_FIELDS) + 4
            x = 0
            for key in LINE_FIELDS:
                string = inv.line_ids._fields[key].string
                if key in LINE_PARAMS:
                    if LINE_PARAMS[key].get("size"):
                        sheet.set_column(x, x, LINE_PARAMS[key]["size"])
                    if LINE_PARAMS[key].get("string"):
                        string = LINE_PARAMS[key]["string"]
                sheet.write(y, x, string, bold)
                x += 1
            # inventory lines
            for line in inv.line_ids:
                x = 0
                y += 1
                for key in LINE_FIELDS:
                    myfield = line[key]
                    if line._fields[key].type in ("many2one", "reference"):
                        if hasattr(line[key], "display_name"):
                            myfield = line[key]["display_name"]
                        elif hasattr(line[key], "name"):
                            myfield = line[key]["name"]
                    sheet.write(y + 1, x, myfield)
                    x += 1
        self._set_notice(workbook)

    def _set_notice(self, workbook):
        sheet = workbook.add_worksheet("notice")
        cell_format = workbook.add_format()
        cell_format.set_text_wrap()
        sheet.set_row(1, 70)
        sheet.set_column(1, 1, 50)
        selection_order = self.env[
            "stock.inventory.line"
        ].get_search_method_strings()
        sheet.write(
            0, 0, _("The following searching order is used in the ERP:")
        )
        sheet.write(1, 1, " - " + "\n - ".join(selection_order), cell_format)

    def _set_format_definition(self, workbook):
        base_format = {"font_size": 10, "text_wrap": True}
        self.format = workbook.add_format(base_format)
        self.emphasis = workbook.add_format(base_format)
        self.emphasis.set_bold()
        self.emphasis.set_top(3)
        self.separator_format = workbook.add_format(base_format)
        self.separator_format.set_top(3)
        self.format.set_text_wrap()
        self.date_format = workbook.add_format(
            {"font_size": 10, "text_wrap": True, "num_format": "dd/mm/yy"}
        )
        self.separator_date_format = workbook.add_format(
            {
                "font_size": 10,
                "text_wrap": True,
                "num_format": "dd/mm/yy",
                "top": 3,
            }
        )
        self.header_format = workbook.add_format(
            {
                "bg_color": "silver",
                "font_size": 10,
                "align": "vcenter",
                "bold": True,
            }
        )
        self.total_format = workbook.add_format(
            {
                "num_format": "# ### ##0.0",
                "bg_color": "orange",
                "align": "center",
                "font_size": 10,
                "bold": True,
            }
        )
