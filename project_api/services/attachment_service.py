# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Mourad EL HADJ MIMOUNE <mourad.el.hadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=consider-merging-classes-inherited

from odoo.addons.component.core import Component


class ExternalAttachmentService(Component):
    _inherit = "base.rest.service"
    _name = "external.attachment.service"
    _collection = "project.project"
    _usage = "attachment"

    @property
    def partner(self):
        return self.work.partner

    def read(self, ids, fields, load):
        # Super is used only to resolve pylint error
        super(ExternalAttachmentService, self).read(ids, fields, load)
        tasks = self.env["project.task"].search(
            [("project_id.partner_id", "=", self.partner.id)]
        )
        attachments = self.env["ir.attachment"].search(
            [
                ("id", "in", ids),
                ("res_id", "in", tasks.ids),
                ("res_model", "=", "project.task"),
            ]
        )
        attachments = attachments.read(fields=fields, load=load)
        if attachments:
            return attachments
        return []

    # Validator
    def _validator_read(self):
        return {
            "ids": {"type": "list"},
            "fields": {"type": "list"},
            "load": {"type": "string"},
            "context": {"type": "dict"},
        }
