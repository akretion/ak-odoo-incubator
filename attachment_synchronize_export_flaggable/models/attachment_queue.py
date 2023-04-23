# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo import models


class AttachmentQueue(models.Model):
    _inherit = "attachment.queue"

    def track_model_import(self, recs):
        recs.write(
            {
                "import_date": datetime.datetime.now(),
                "import_file_id": self.id,
            }
        )
