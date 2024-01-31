# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rental_duration = fields.Boolean(
        string="Rental Duration",
        related="company_id.rental_duration",
        readonly=False,
        )
    rental_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Rental Uom",
        related="company_id.rental_uom_id",
        readonly=False,
        )
