# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    exclusive = fields.Selection(
        selection_add=[
            ("proposals", "Call for Proposals (non-exclusive)"),
        ],
        ondelete={"proposals": "cascade"},
    )

    company_id = fields.Many2one(
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
        readonly=True,
    )

    multi_company_selection = fields.Selection(
        selection=[
            ("no", "No"),
            ("selected", "Selected Companies"),
            ("all", "All Companies"),
        ],
        string="Multi Company Selection",
        default="no",
    )

    company_to_call_ids = fields.Many2many(
        comodel_name="res.company",
        string="Companies To Call",
    )

    def _default_proposal_template_id(self):
        return self.env.ref(
            "purchase_requisition_proposal.mail_template_requisition_proposal",
            raise_if_not_found=False,
        )

    proposal_template_id = fields.Many2one(
        "mail.template",
        default=lambda self: self._default_proposal_template_id(),
        string="Opening Report Template",
        required=True,
    )

    def _default_proposal_result_template_id(self):
        return self.env.ref(
            "purchase_requisition_proposal.mail_template_result_proposal",
            raise_if_not_found=False,
        )

    proposal_result_template_id = fields.Many2one(
        "mail.template",
        default=lambda self: self._default_proposal_result_template_id(),
        string="Closure Email Template",
        required=True,
    )
