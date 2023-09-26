# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class MailTemplatePreview(models.TransientModel):
    _inherit = "mail.template.preview"

    layout_id = fields.Many2one(
        "ir.ui.view",
        "Layout",
    )
    layout_domain = fields.Char(compute="_compute_layout_domain")

    def send(self):
        xml_id = self.layout_id.get_external_id()[self.layout_id.id]
        self.mail_template_id.with_context(force_mail_uniq_layout_id=xml_id).send_mail(
            self.model_id.id
        )

    def _get_layout_domain(self):
        return []

    @api.depends("mail_template_id")
    def _compute_layout_domain(self):
        for record in self:
            record.layout_domain = json.dumps(self._get_layout_domain())
