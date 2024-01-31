# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    must_have_duration = fields.Boolean(related="product_id.must_have_duration")

    end_date = fields.Date(
        compute="_compute_end_date",
        store=True,
        readonly=False,
    )


    # Here we avoid sol qty check.
    # TODO: change the code in sale_rental module after
    # its migration, to work with other uom than days.
    def _check_sale_line_rental(self):
        for line in self:
            try:
                super(SaleOrderLine, line)._check_sale_line_rental()
            except ValidationError as e:
                if "multiplied by the Rental Quantity" in str(e) and line.must_have_duration:
                    pass
                else:
                    raise

    @api.depends("start_date", "product_uom_qty")
    def _compute_end_date(self):
        for rec in self:
            if rec.product_id.must_have_duration and rec.product_uom_qty and rec.start_date:
                rec.end_date = rec.start_date + relativedelta(months=rec.product_uom_qty * rec.product_uom.factor)

    def _compute_number_of_days(self):
        for rec in self:
            if rec.product_id.must_have_duration:
                pass
            else:
                return super()._compute_number_of_days()



    def open_rental_line_wizard(self):
        res = super().open_rental_line_wizard()
        wizard = self.env["sale.rental.line.wizard"].browse(res["res_id"])
        wizard.rental_duration = self.product_uom_qty
        return res
