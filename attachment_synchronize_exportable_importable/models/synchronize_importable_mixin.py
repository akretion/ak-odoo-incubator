# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import fields, models


class SynchronizeImportableMixin(models.AbstractModel):
    _name = "synchronize.importable.mixin"

    import_date = fields.Date()
    import_file_id = fields.Many2one("attachment.queue")

    def track_import_date(self):
        self.import_date = datetime.datetime.now()

    def track_imported_through(self, attachment):
        self.import_file = attachment.id
