# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv.expression import AND


class AttachmentSynchronizeTask(models.Model):
    _inherit = "attachment.synchronize.task"

    def _send_to_backend(self, file, filename, flow):
        return getattr(self, "_send_to_backend_{}".format(flow))(file, filename)

    def scheduler_export_flagged(self, model):
        recs = self.env[model].search([("export_flag", "=", True)])
        attachments = recs.synchronize_export()
        self._send_to_backend(attachments)

    def scheduler_export_unexported(self, model, domain=False):
        if not domain:
            domain = []
        domain = AND([("export_date", "=", False), domain])
        recs = self.env[model].search(domain)
        attachments = recs.synchronize_export()
        self._send_to_backend(attachments)
