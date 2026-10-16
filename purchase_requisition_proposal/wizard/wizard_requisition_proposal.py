# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RequisitionProposalWizard(models.TransientModel):
    _name = "requisition.proposal.wizard"
    _description = "Requisition Proposal Wizard"

    requisition_line_id = fields.Many2one(
        "purchase.requisition.line", required=True, string="Purchase Agreement Line"
    )

    proposal_line_ids = fields.Many2many(
        comodel_name="purchase.requisition.proposal",
        string="Proposal Line",
    )

    def confirm_lines(self):
        for line in self.proposal_line_ids:
            proposal_line = self.env["purchase.requisition.proposal"].browse(line.id)
            proposal_line.write(
                {
                    "requisition_line_id": self.requisition_line_id.id,
                }
            )
