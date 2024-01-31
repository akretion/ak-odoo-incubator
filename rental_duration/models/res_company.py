# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"


    rental_duration = fields.Boolean(
        string="Rental Duration",
        )
    rental_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Rental Uom",
        )
