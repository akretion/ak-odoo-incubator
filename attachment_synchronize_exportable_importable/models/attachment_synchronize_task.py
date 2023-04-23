# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
# from odoo import models
#
#
# class AttachmentSynchronizeTask(models.Model):
#     _inherit = "attachment.synchronize.task"
#
#     def _send_to_backend(self, file, filename, flow):
#         return getattr(self, "_send_to_backend_{}".format(flow))(file, filename)
#
#     def scheduler_export_flagged(self, model):
#         recs = self.env[model].search([("export_flag", "=", True)])
#         file, filename = recs.synchronize_export()
#         self._send_to_backend(file, filename)
#
#     def scheduler_export_flow(self, model, flow):
#         domain = self._get_domain_for(flow)
#         recs = self.env[model].search(domain)
#         attachment = recs.synchronize_export()
#         self._send_to_backend(attachment, flow)
#
#     def _get_domain_for(self, flow):
#         return [()]
