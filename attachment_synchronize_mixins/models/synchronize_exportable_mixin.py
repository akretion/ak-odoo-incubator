# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv
import datetime
import uuid
from io import StringIO

from odoo import fields, models


class SynchronizeExportableMixin(models.AbstractModel):
    _name = "synchronize.exportable.mixin"
    export_date = fields.Date()
    export_attachment = fields.Char()
    export_date_processed = fields.Date()
    export_flag = fields.Boolean()

    @property
    def sync_fields(self):
        return []

    def write(self, vals):
        fields_changed = list(vals.keys())
        for field_trigger in self.sync_fields:
            if field_trigger in fields_changed:
                self.export_flag = True
        return super().write(vals)

    def track_date_processed(self, date):
        self.export_date_processed = date

    def track_export(self, attachment):
        self.export_date = datetime.datetime.now()
        self.export_attachment = attachment

    def synchronize_export(self):
        data = self._prepare_export_data()
        attachment = self._format_to_exportfile(data)
        self.track_export(attachment)
        self.export_flag = False
        return attachment

    def _prepare_export_data(self) -> list:
        raise NotImplementedError

    def _format_to_exportfile(self, data):
        return self._format_to_exportfile_csv(data)

    def _format_to_exportfile_csv(self, data):
        csv_file = StringIO()
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        csv_file.seek(0)
        return self.env["attachment.queue"].create(
            {
                "name": self._get_export_name(),
                "datas": base64.b64encode(csv_file.getvalue().encode("utf-8")),
            }
        )

    def _get_export_name(self):
        return str(uuid.uuid4())
