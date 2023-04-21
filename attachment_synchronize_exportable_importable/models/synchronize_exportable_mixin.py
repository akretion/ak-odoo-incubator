# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import fields, models

from .helpers import format_export_to_csv


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
        for mode, field_trigger in self.sync_fields:
            if field_trigger in fields_changed:
                self.export_flag = True
        return super().write(vals)

    def track_export_date(self):
        self.export_date = datetime.datetime.now()

    def track_export_attachment(self, attachment):
        self.export_attachment = attachment

    def track_date_processed(self, date):
        self.export_date_processed = date

    def set_flag_export(self):
        self.export_flag = True

    def unset_flag_export(self):
        self.export_flag = False

    def synchronize_export(self, **kwargs):
        data = self._prepare_export_data(**kwargs)
        attachment = self._format_to_exportfile(data, **kwargs)
        self._postprocess_export(data, attachment **kwargs)
        self.track_export_date()
        self.track_export_attachment(attachment)
        self.unset_flag_export()
        return attachment

    def _prepare_export_data(self, mode=False, **kwargs) -> dict:
        try:
            fn = getattr(self, "_prepare_export_data_" + mode)(**kwargs)
        except AttributeError:
            data = {}
            self._map_data_simple(data)
            self._map_data_process(data)
            return data
        return fn(**kwargs)

    def _format_to_exportfile(self, data, fmt=False, **kwargs):
        try:
            fn = getattr(self, "_format_to_exportfile_" + fmt)(data, **kwargs)
        except AttributeError:
            return format_export_to_csv(data)
        return fn(data, **kwargs)

    def _postprocess_export(self, data, file, filename, fname=False, **kwargs):
        try:
            fn = getattr(self, "_postprocess_export_" + fname)
        except AttributeError:
            return
        return fn(data, file, filename, **kwargs)

    # Helpers for _prepare_export_data

    @property
    def fields_map_simple(self):
        return []

    @property
    def fields_map_process(self):
        return []

    def _map_data_simple(self, data: dict):
        for field_file, field_odoo in self.fields_map_simple:
            data[field_file] = self[field_odoo]

    def _map_data_process(self, data: dict):
        for field, fn in self.fields_map_process:
            data[field] = getattr(self, fn)()
