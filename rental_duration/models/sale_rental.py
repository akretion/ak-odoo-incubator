# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class SaleRental(models.Model):
    _inherit = "sale.rental"

    rental_duration = fields.Float(
        related="start_order_line_id.product_uom_qty", readonly=True, store=True
        )
    rental_duration_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Rental Duration UoM",
        related="start_order_line_id.product_uom"
        )
