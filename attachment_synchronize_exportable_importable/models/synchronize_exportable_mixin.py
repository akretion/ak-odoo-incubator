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
        for field_trigger in self.sync_fields:
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
        if kwargs.get("export_flow"):
            self = self.with_context(export_flow=kwargs["export_flow"])
        data = self._prepare_export_data()
        attachment = self._format_to_exportfile(data)
        self._postprocess_export(data, attachment)
        self.track_export_date()
        self.track_export_attachment(attachment)
        self.unset_flag_export()
        return attachment

    def _prepare_export_data(self) -> list:
        try:
            fn = getattr(
                self,
                "_prepare_export_data_{}".format(str(self.env.context.get("flow"))),
            )
        except AttributeError:
            res = []
            for rec in self:
                data = rec._export_map_fields()
                res += data
            return res
        return fn()

    def _default_prepare_export_data(self):
        res = []
        for rec in self:
            data = rec._export_map_fields()
            res += data
        return res

    def _export_map_fields(self):
        res = {}
        res.update(self._map_data_simple())
        res.update(self._map_data_process())
        return [res]

    def _format_to_exportfile(self, data, fmt=False):
        try:
            fn = getattr(self, "_format_to_exportfile_" + fmt)(data)
        except AttributeError:
            return format_export_to_csv(data)
        return fn(data)

    def _postprocess_export(self, data, file, filename, fname=False):
        try:
            fn = getattr(self, "_postprocess_export_" + fname)
        except AttributeError:
            return
        return fn(data, file, filename)

    # Helpers for _prepare_export_data

    @property
    def fields_map_simple(self):
        return []

    @property
    def fields_map_process(self):
        return {}

    def _map_data_simple(self):
        res = {}
        for field_file, field_odoo in self.fields_map_simple():
            res[field_file] = self[field_odoo]
        return res

    def _map_data_process(self):
        res = {}
        for field, fn in self.fields_map_process().items():
            res[field] = getattr(self, fn)()
        return res
