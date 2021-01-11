# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class IrRule(models.Model):
    _inherit = "ir.rule"

    def _ensure_install_mode(self):
        if not self._context.get("install_mode"):
            raise UserError(_("Rule are not editable, put your rule in your code"))

    @api.model_create_multi
    def create(self, vals_list):
        self._ensure_install_mode()
        return super().create(vals_list)

    def write(self, vals):
        self._ensure_install_mode()
        return super().write(vals)
