# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_requisition_id = fields.Many2one(
        comodel_name="purchase.requisition",
        string="Purchase Requisition",
        related="auto_purchase_order_id.requisition_id",
    )

    def action_confirm(self):
        for order in self.filtered("auto_purchase_order_id"):
            if order.purchase_requisition_id.exclusive == "proposals":
                for line in order.order_line.sudo():
                    line.price_unit = line.auto_purchase_line_id.price_unit
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    requirement_proposal_id = fields.Many2one(
        comodel_name="purchase.requisition.proposal",
        string="From Proposal",
        related="auto_purchase_line_id.requirement_proposal_id",
    )
