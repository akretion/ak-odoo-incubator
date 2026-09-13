# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    access_type = fields.Selection(
        selection=[
            ("no_access", "No Access"),
            ("read", "Read Only"),
            ("write", "Read and Write"),
            ("create", "Read, Write and Create"),
            ("full", "Full Access"),
            ("other", "Other Combination of access rights"),
        ],
        string="Access Type",
        compute="_compute_access_type",
        store=True,
    )

    @api.depends("perm_read", "perm_write", "perm_create", "perm_unlink")
    def _compute_access_type(self):
        for rec in self:
            if (
                not rec.perm_read
                and not rec.perm_write
                and not rec.perm_create
                and not rec.perm_unlink
            ):
                rec.access_type = "no_access"
            elif (
                rec.perm_read
                and not rec.perm_write
                and not rec.perm_create
                and not rec.perm_unlink
            ):
                rec.access_type = "read"
            elif (
                rec.perm_read
                and rec.perm_write
                and not rec.perm_create
                and not rec.perm_unlink
            ):
                rec.access_type = "write"
            elif (
                rec.perm_read
                and rec.perm_write
                and rec.perm_create
                and not rec.perm_unlink
            ):
                rec.access_type = "create"
            elif (
                rec.perm_read and rec.perm_write and rec.perm_create and rec.perm_unlink
            ):
                rec.access_type = "full"
            else:
                rec.access_type = "other"
