# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import fields, models


class SynchronizeImportableMixin(models.AbstractModel):
    _name = "synchronize.importable.mixin"

    import_date = fields.Serialized()
    import_file_ids = fields.Serialized()

    def track_import_date(self, mode):
        self.import_date[mode] = datetime.datetime.now()

    def track_imported_through(self, mode, attachment):
        self.import_file[mode] = attachment.id
