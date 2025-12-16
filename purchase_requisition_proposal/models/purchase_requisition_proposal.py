# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequisitionProposal(models.Model):
    _inherit = ["purchase.requisition.information.mixin"]
    _name = "purchase.requisition.proposal"
    _description = "Purchase Requisition Proposal"
    _order = "requisition_line_id"

    name = fields.Char(
        string="Name",
    )

    requisition_id = fields.Many2one(
        "purchase.requisition", string="Purchase Agreement"
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase",
    )
    requisition_line_id = fields.Many2one(
        "purchase.requisition.line", required=True, string="Purchase Agreement Line"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        # related="requisition_id.partner_id"
    )
    company_id = fields.Many2one(
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
        readonly=True,
    )
    requisition_company_id = fields.Many2one(
        string="Company", related="requisition_id.company_id", readonly=True
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    product_id = fields.Many2one(
        "product.product", string="Product", related="requisition_line_id.product_id"
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="UoM",
        domain="[('category_id', '=', product_uom_category_id)]",
        related="requisition_line_id.product_uom_id",
        readonly=True,
    )
    price_unit = fields.Float(
        string="Unit Price",
        digits="Product Price",
        related="requisition_line_id.price_unit",
        readonly=True,
    )
    product_qty = fields.Float(
        string="Requested Qty",
        digits="Product Unit of Measure",
        related="requisition_line_id.product_qty",
        readonly=True,
    )
    schedule_date = fields.Date(
        string="Requested Date", required=True, related="requisition_id.schedule_date"
    )
    qty_proposed = fields.Float(
        string="Proposed Qty",
        digits="Product Unit of Measure",
        default=lambda self: self.product_qty,
    )
    qty_planned = fields.Float(
        string="Planned Qty",
        digits="Product Unit of Measure",
        default=lambda self: self.product_qty,
    )
    date_planned = fields.Date(string="Proposed Date")

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code(
            "purchase.requisition.proposal"
        )
        return super().create(vals)

    @api.constrains("qty_planned")
    def _check_company_id_date_range_id(self):
        for rec in self:
            if rec.qty_planned > rec.qty_proposed:
                raise ValidationError(
                    _(
                        "Selected Quantity can not be superior than "
                        "Proposed Quantity."
                    )
                )

    def duplicate_line(self):
        self.create(
            {
                "requisition_id": self.requisition_id.id,
                "requisition_line_id": self.requisition_line_id.id,
                "product_id": self.product_id.id,
                "partner_id": self.partner_id.id,
            }
        )
        return self.requisition_line_id.show_requisition_proposal_line()

    def remove_line(self):
        req_line = self.requisition_line_id
        self.unlink()
        return req_line.show_requisition_proposal_line()
