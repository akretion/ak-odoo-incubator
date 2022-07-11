# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrUiViewCustom(models.Model):
    _inherit = "ir.ui.view.custom"

    shared = fields.Boolean(default=False, string="Shared")
