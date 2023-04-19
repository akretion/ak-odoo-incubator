# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AttachmentSynchronizeTask(models.Model):
    _inherit = "attachment.synchronize.task"

    def _send_to_backend(self, file, filename, mode):
        return getattr(self, "_send_to_backend_{}".format(mode))(file, filename, mode)

    def scheduler_export(self, model, mode):
        recs = self.env[model].search([("export_flag", "ilike", "{}:".format(mode))])
        file, filename = recs.synchronize_export(mode)
        self._send_to_backend(file, filename, mode)
