# Copyright 2023 Akretion (https://www.akretion.com).
# @author Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    force_fiscal_position_id = fields.Many2one("account.fiscal.position")
