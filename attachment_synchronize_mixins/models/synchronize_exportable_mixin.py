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
    _description = "Synchronizable export mixin"
    export_date = fields.Date()
    export_attachment = fields.Char()
    export_flag = fields.Boolean()

    def synchronize_export(self):
        data = self._prepare_export_data()
        if not data:
            return self.env["attachment.queue"]
        attachment = self._format_to_exportfile(data)
        self.track_export(attachment)
        self.export_flag = False
        return attachment

    def track_export(self, attachment):
        self.export_date = datetime.datetime.now()
        self.export_attachment = attachment

    def _prepare_export_data(self) -> list:
        raise NotImplementedError

    def _format_to_exportfile(self, data):
        return self._format_to_exportfile_csv(data)

    def _format_to_exportfile_csv(self, data):
        csv_file = StringIO()
        delimiter = self.env.context.get("csv_delimiter") or ";"
        writer = csv.DictWriter(
            csv_file, fieldnames=data[0].keys(), delimiter=delimiter
        )
        for row in data:
            writer.writerow(row)
        csv_file.seek(0)
        ast = self.env.context.get("attachment_task")
        vals = {
            "name": self._get_export_name(),
            "datas": base64.b64encode(csv_file.getvalue().encode("utf-8")),
            "task_id": ast.id,
            "file_type": ast.file_type,
        }
        return self.env["attachment.queue"].create(vals)

    def _get_export_name(self):
        return str(uuid.uuid4())
