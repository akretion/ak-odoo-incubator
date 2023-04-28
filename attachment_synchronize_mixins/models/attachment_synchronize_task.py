# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import models
from odoo.osv.expression import AND


class AttachmentSynchronizeTask(models.Model):
    _inherit = "attachment.synchronize.task"

    def scheduler_export_flagged(self, model):
        recs = self.env[model].search([("export_flag", "=", True)])
        attachments = recs.with_context(attachment_task=self).synchronize_export()
        self.send_to_backend(attachments)

    def scheduler_export_unexported(self, model, domain=False):
        if not domain:
            domain = [("export_date", "=", False)]
        else:
            domain = AND([[("export_date", "=", False)], domain])
        recs = self.env[model].search(domain)
        attachments = recs.with_context(attachment_task=self).synchronize_export()
        self.send_to_backend(attachments)

    def send_to_backend(self, attachment):
        self.backend_id.add(attachment.name, base64.b64decode(attachment.datas))
