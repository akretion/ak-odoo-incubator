# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_sale_order_line_data(self, purchase_line, dest_company, sale_order):
        res = super()._prepare_sale_order_line_data(
            purchase_line, dest_company, sale_order
        )
        res["price_unit"] = purchase_line.price_unit
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    requirement_proposal_id = fields.Many2one(
        comodel_name="purchase.requisition.proposal",
        string="Requirement Proposal",
    )
