# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
#
# from odoo import models
#
# from .helpers import format_export_to_csv
#
#
# class SynchronizeExportableMixin(models.AbstractModel):
#     _name = "synchronize.exportable.mixin"
#
#     def _default_prepare_export_data(self):
#         res = []
#         for rec in self:
#             data = rec._export_map_fields()
#             res += data
#         return res
#
#     def _export_map_fields(self):
#         res = {}
#         res.update(self._map_data_simple())
#         res.update(self._map_data_process())
#         return [res]
#
#     @property
#     def fields_map_simple(self):
#         return []
#
#     @property
#     def fields_map_process(self):
#         return {}
#
#     def _map_data_simple(self):
#         res = {}
#         for field_file, field_odoo in self.fields_map_simple():
#             res[field_file] = self[field_odoo]
#         return res
#
#     def _map_data_process(self):
#         res = {}
#         for field, fn in self.fields_map_process().items():
#             res[field] = getattr(self, fn)()
#         return res
#
#     def _format_to_exportfile(self, data, fmt=False):
#         try:
#             fn = getattr(self, "_format_to_exportfile_" + fmt)(data)
#         except AttributeError:
#             return format_export_to_csv(data)
#         return fn(data)
#
#     def _postprocess_export(self, data, file, filename, fname=False):
#         try:
#             fn = getattr(self, "_postprocess_export_" + fname)
#         except AttributeError:
#             return
#         return fn(data, file, filename)
