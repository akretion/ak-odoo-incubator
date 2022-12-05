#  Copyright (C) 2021 Akretion (http://www.akretion.com).

import base64

from odoo import api, fields, models

from odoo.addons.web.controllers.export import CSVExport, ExcelExport


class IrExportsConfig(models.Model):
    _name = "ir.exports.config"
    _description = "Make export more configurable"

    name = fields.Char(required=True)
    export_id = fields.Many2one("ir.exports")
    filename = fields.Char(
        help="Exported File will be renamed to this name "
        "If left empty, by default, the name of the file will be : "
        "{YYYY-MM-DD}_{export name}.{format}"
    )
    additional_export_line_ids = fields.One2many(
        "additional.export.line",
        "export_config_id",
        string="Additional Data",
        help="You can add static custom data here",
    )
    file_format = fields.Selection(
        selection=[("csv", "CSV"), ("xlsx", "Excel")],
        default="csv",
        required=True,
    )
    resource = fields.Char(related="export_id.resource", store=True, readonly=True)
    visible_configurable_data_fields = fields.Boolean(
        compute="_compute_visible_configurable_data_fields",
        help="Hide the fields export_id and additional_export_line_ids depending "
        "one the file format",
    )

    def _is_visible_configurable_data(self):
        if self.file_format in ("csv", "xlsx"):
            return True
        return False

    @api.depends("file_format")
    def _compute_visible_configurable_data_fields(self):
        for rec in self:
            rec.visible_configurable_data_fields = rec._is_visible_configurable_data()

    def get_file_name(self, records, res_id=False, res_model=False):
        # override to put a specific name, that could depend on records or res_id
        # for instance
        self.ensure_one()
        today = fields.Date.to_string(fields.Date.today())
        return self.filename or "{today}_{name}.{format}".format(
            today=today, name=self.name, format=self.file_format
        )

    def get_attachment(self, records, res_id=False, res_model=False):
        """
        Optional res_id and res_model to attach the attachment on a specific record
        # by default it will be attach to the related export config
        """
        self.ensure_one()
        data = self.get_file(records)
        data = base64.b64encode(data)
        filename = self.get_file_name(records, res_id=res_id, res_model=res_model)
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "type": "binary",
                "res_id": res_id or self.id,
                "res_model": res_model or self._name,
                "datas": data,
            }
        )
        return attachment

    def get_file(self, records):
        function = "_get_file_{format}".format(format=self.file_format or "")
        if not hasattr(self, function):
            raise NotImplementedError(
                "Format {format} is not implementer".format(format=self.file_format)
            )
        data = getattr(self, function)(records)
        return data

    def _get_file_csv(self, records):
        header, rows = self.get_data_from_export_model(records)
        return CSVExport().from_data(header, rows)

    def _get_file_xlsx(self, records):
        header, rows = self.get_data_from_export_model(records)
        return ExcelExport().from_data(header, rows)

    def get_data_from_export_model(self, records):
        tech_names, display_names = self.get_field_names()
        rows = records.export_data(tech_names).get("datas", [])
        # we have to loop on each row to add the additional_data
        all_display_names, all_rows = self.merge_additional_data(
            display_names, rows, records
        )
        return all_display_names, all_rows

    def get_field_names(self):
        field_technames = []
        field_names = []
        for line in self.export_id.export_fields:
            field_technames.append(line.name)
            field_names.append(line.field_description or line.name)
        # in case we want to add more data in rows not directly coming from record
        # fields, we do this trick : we add a dummy record field at then end of
        # the fields list. It will allow us to know, for each rows, if it is a main
        # row or a sub row (because of x2many fields)
        # so we will check if this dummy if field is filled and in that case, add
        # the additional values, in other cases, it will be x2many fields and we
        # won't do anything
        if self.additional_export_line_ids:
            field_technames.append("id")
            field_names.append("Is main row")
        return field_technames, field_names

    def get_additional_display_names(self):
        display_names = []
        for line in self.additional_export_line_ids:
            display_names.append(line.field_description)
        return display_names

    def merge_additional_data(self, display_names, rows, records):
        if not self.additional_export_line_ids:
            return display_names, rows
        additional_display_names = self.get_additional_display_names()
        # remove last dummy field used to know if row is a main row or a x2many row
        display_names.pop()
        all_display_names = display_names + additional_display_names

        index = 0
        for row in rows:
            # last item is the id of the record meaning it is a main row and not a
            # x2many row. We merge additional value only in main rows
            if row[-1]:
                record = records[index]
                index += 1
                # remove dummy id value used to know if it is a main or x2many row
                row.pop()
                row += self.get_additional_values(record)
        return all_display_names, rows

    def get_additional_values(self, record):
        # Override this to implement your own way to get some specific data not
        # not available on classic record fields.
        additional_data = []
        self.ensure_one()
        for additional_export_line in self.additional_export_line_ids:
            additional_data.append(additional_export_line.value or "")
        return additional_data


class AdditionalExportLine(models.Model):
    _name = "additional.export.line"
    _order = "sequence,id"
    _description = "Additional data in exports, not coming directly from a field"

    export_config_id = fields.Many2one("ir.exports.config", "Export", required=True)
    sequence = fields.Integer()
    field_description = fields.Char()
    value = fields.Char()
