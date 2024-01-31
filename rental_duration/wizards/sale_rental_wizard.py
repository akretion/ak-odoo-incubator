# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from dateutil.relativedelta import relativedelta

class SaleRentalLineWizard(models.TransientModel):
    _inherit = "sale.rental.line.wizard"

    rental_duration = fields.Integer(
        string="Rental Duration",
        )

    rental_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Rental Uom",
        related="rental_line_id.product_uom"
        )

    must_have_duration = fields.Boolean(related="rental_line_id.must_have_duration")

    def confirm_rental_config(self):
        res = super().confirm_rental_config()
        line = self.rental_line_id
        end = self.start_date + relativedelta(months=self.rental_duration * self.rental_uom_id.factor)
        line.write(
            {
                "product_uom_qty": self.rental_duration,
                "end_date": end,
            }
        )
        return res
