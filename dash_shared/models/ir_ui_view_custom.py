# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrUiViewCustom(models.Model):
    _inherit = "ir.ui.view.custom"

    shared = fields.Boolean(default=False, string="Shared")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ref = [ref[2] for ref in args if ref[0] == "ref_id" and len(args) != 1]
        if ref and ref[0] and self.search([("ref_id", "=", ref[0])], limit=1).shared:
            args = [("ref_id", "=", ref[0])]
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )
