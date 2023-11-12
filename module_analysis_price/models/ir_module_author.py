# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrModuleAuthor(models.Model):
    _inherit = "ir.module.author"

    community_installed_module_qty = fields.Integer(
        compute="_compute_community_rate", store=True
    )
    community_installed_module_rate = fields.Float(
        compute="_compute_community_rate", store=True
    )
    community_installed_code_qty = fields.Integer(
        compute="_compute_community_rate", store=True
    )
    community_installed_code_rate = fields.Float(
        compute="_compute_community_rate", store=True
    )

    @api.depends(
        "module_ids.code_qty",
        "module_ids.module_type_id.source",
    )
    def _compute_community_rate(self):
        type_community = self.env["ir.module.type"].search(
            [("source", "=", "community")]
        )
        total_code_qty = sum(type_community.mapped("code_qty"))
        total_module_qty = sum(type_community.mapped("installed_module_qty"))
        if total_module_qty:
            for record in self:
                installed_module_ids = record.module_ids.filtered(
                    lambda l: l.state == "installed"
                )
                modules = installed_module_ids.filtered(
                    lambda m: m.module_type_id.source == "comunity"
                )
                record.community_installed_code_qty = sum(modules.mapped("code_qty"))
                record.community_installed_code_rate = (
                    100 * sum(modules.mapped("code_qty")) / total_code_qty
                )
                record.community_installed_module_qty = len(modules)
                record.community_installed_module_rate = (
                    100 * len(modules) / total_module_qty
                )
        else:
            for record in self:
                record.community_installed_code_qty = 0
                record.community_installed_code_rate = 0
                record.community_installed_module_qty = 0
                record.community_installed_module_rate = 0
