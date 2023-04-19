# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import fields, models

from .helpers import format_export_to_csv


class SynchronizeExportableMixin(models.AbstractModel):
    _name = "synchronize.exportable.mixin"
    export_date = fields.Serialized()
    export_filename = fields.Serialized()
    export_date_processed = fields.Serialized()
    export_flag = fields.Serialized()

    @property
    def sync_fields(self):
        """Format as in mode:[fields]"""
        return {}

    def write(self, vals):
        fields_changed = list(vals.keys())
        for mode, field_trigger in self.sync_fields.items():
            if field_trigger in fields_changed:
                self.export_flag[mode].update({mode: True})
        return super().write(vals)

    def track_export_date(self, flow):
        self.export_date[flow] = datetime.datetime.now()

    def track_export_filename(self, flow, filename):
        self.export_filename[flow] = filename

    def track_date_processed(self, flow, date):
        self.export_date_processed[flow] = date

    def set_flag_export(self, flow):
        self.export_flag[flow] = True

    def unset_flag_export(self, flow):
        self.export_flag[flow] = False

    def synchronize_export(self, mode, **kwargs):
        data = self._prepare_export_data(mode, **kwargs)
        file, filename = self._format_to_exportfile(mode, data, **kwargs)
        self._postprocess_export(mode, data, file, filename, **kwargs)
        self.track_export_date(mode)
        self.track_export_filename(mode, filename)
        self.unset_flag_export(mode)
        return file, filename

    def _prepare_export_data(self, mode=False, **kwargs) -> list:
        try:
            fn = getattr(self, "_prepare_export_data_" + mode)(**kwargs)
        except AttributeError:
            data = {}
            self._map_data_simple(data, mode)
            self._map_data_process(data, mode)
            return data
        return fn(**kwargs)

    def _format_to_exportfile(self, data, mode=False, **kwargs):
        try:
            fn = getattr(self, "_format_to_exportfile_" + mode)(data, **kwargs)
        except AttributeError:
            return format_export_to_csv(data)
        return fn(data, **kwargs)

    def _postprocess_export(self, data, file, filename, mode=False, **kwargs):
        try:
            fn = getattr(self, "_postprocess_export_" + mode)
        except AttributeError:
            return
        return fn(data, file, filename, **kwargs)

    # Helpers for _prepare_export_data

    @property
    def fields_map_simple(self):
        """
        Format as:
        {mode:{field_in_file: odoo_field}} for direct copy
        """
        return {}

    @property
    def fields_map_process(self):
        """
        Format as:
        {mode:{field_in_file: function}}
        """
        return {}

    def _map_data_simple(self, data: dict, mode: str):
        for field_file, field_odoo in self.fields_map_simple[mode].items():
            data[field_file] = self[field_odoo]

    def _map_data_process(self, data: dict, mode: str):
        for field, fn in self.fields_map_process[mode].items():
            data[field] = getattr(self, fn)()
