# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseRequisitionInformationMixin(models.AbstractModel):
    _name = "purchase.requisition.information.mixin"
    _description = "Purchase Requisition Information Mixin"

    date_check = fields.Selection(
        selection=[
            ("respected", "Respected"),
            ("not_respected", "Not Respected"),
            ("none", ""),
        ],
        string="Date Check",
        compute="_compute_date_check",
    )

    qty_check = fields.Selection(
        selection=[
            ("enough", "Enough"),
            ("not_enough", "Not Enough"),
            ("none", ""),
        ],
        string="Qty Check",
        compute="_compute_qty_check",
    )

    @api.depends("schedule_date", "date_planned")
    def _compute_date_check(self):
        for rec in self:
            if rec.schedule_date and rec.date_planned:
                if rec.schedule_date >= rec.date_planned:
                    rec.date_check = "respected"
                else:
                    rec.date_check = "not_respected"
            else:
                rec.date_check = "none"

    @api.depends("product_qty", "qty_planned")
    def _compute_qty_check(self):
        for rec in self:
            if rec.product_qty == 0:
                rec.qty_check = "none"
            elif rec.qty_planned >= rec.product_qty:
                rec.qty_check = "enough"
            else:
                rec.qty_check = "not_enough"
