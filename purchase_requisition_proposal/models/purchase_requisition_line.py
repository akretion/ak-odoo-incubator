# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = ["purchase.requisition.line", "purchase.requisition.information.mixin"]
    _name = "purchase.requisition.line"

    proposal_line_ids = fields.One2many(
        "purchase.requisition.proposal", "requisition_line_id", string="proposal Lines"
    )
    proposal_line_count = fields.Integer(compute="_compute_proposal_line_count")
    qty_planned = fields.Float(
        compute="_compute_planned_qty", string="Planned Quantities"
    )
    date_planned = fields.Date(string="Proposed Date", compute="_compute_date_planned")
    is_proposal_line_validate = fields.Boolean(
        string="Is Line Validate",
        default=False,
    )

    @api.depends("proposal_line_ids.date_planned")
    def _compute_date_planned(self):
        for rec in self:
            date_planned_list = [
                line.date_planned
                for line in rec.proposal_line_ids
                if line.qty_planned and line.date_planned
            ]
            if date_planned_list:
                rec.date_planned = max(date_planned_list)
            else:
                rec.date_planned = False

    @api.depends("proposal_line_ids")
    def _compute_proposal_line_count(self):
        for rec in self:
            rec.proposal_line_count = len(
                [line for line in rec.proposal_line_ids if line.qty_proposed]
            )

    def create_proposal(self):
        self.sudo().write({"is_proposal_line_validate": True})
        self.env["purchase.requisition.proposal"].create(
            {
                "requisition_id": self.requisition_id.id,
                "requisition_line_id": self.id,
                "product_id": self.product_id.id,
                "qty_proposed": self.product_qty,
                "date_planned": self.schedule_date,
                "partner_id": self.env.company.partner_id.id,
            }
        )

    def create_and_modify_proposal(self):
        self.create_proposal()
        return self.show_requisition_proposal_line()

    def show_requisition_proposal_line(self):
        if self.env.company == self.requisition_id.company_id:
            domain = [("requisition_line_id", "=", self.id)]
            context = {"received_proposal": True}
            view = self.env.ref(
                "purchase_requisition_proposal.requisition_proposal_wizard"
            )
        else:
            domain = [
                ("requisition_line_id", "=", self.id),
                ("partner_id", "=", self.env.user.company_id.partner_id.id),
            ]
            view = self.env.ref(
                "purchase_requisition_proposal.requisition_proposal_buttons_wizard"
            )
            context = {"my_proposal": True, "active_id": self.id,}
        # return {
        #     "name": _("proposals"),
        #     "type": "ir.actions.act_window",
        #     "view_mode": "form",
        #     "res_model": "purchase.requisition.proposal",
        #     "target": "new",
        #     "domain": domain,
        #     "context": context,
        #     "view_id": view.id,
        # }

        wizard = self.env["requisition.proposal.wizard"].create(
            {
                "requisition_line_id": self.id,
                "proposal_line_ids": self.proposal_line_ids.filtered_domain(domain).ids,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "requisition.proposal.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "view_id": view.id,
            "target": "new",
            "context": context,
        }


    @api.depends("proposal_line_ids.qty_planned")
    def _compute_planned_qty(self):
        for rec in self:
            rec.qty_planned = sum(rec.proposal_line_ids.mapped("qty_planned"))
