# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    exclusive = fields.Selection(related="type_id.exclusive", readonly=True)
    schedule_date = fields.Date(required=True)
    date_end = fields.Date(required=True)
    requisition_proposal_ids = fields.One2many(
        comodel_name="purchase.requisition.proposal",
        inverse_name="requisition_id",
        string="Requisition proposal",
    )
    requisition_proposal_count = fields.Integer(
        compute="_compute_requisition_proposal_count"
    )
    company_to_call_ids = fields.Many2many(
        comodel_name="res.company",
        compute="_compute_company_to_call_ids",
        string="Companies To Call",
        readonly=False,
        store=True,
    )

    @api.depends("exclusive")
    def _compute_company_to_call_ids(self):
        for rec in self:
            if (
                rec.exclusive == "proposals"
                and rec.type_id.multi_company_selection != "no"
            ):
                if rec.type_id.multi_company_selection == "selected":
                    rec.company_to_call_ids = rec.type_id.company_to_call_ids
                else:
                    rec.company_to_call_ids = rec.env["res.company"].search(
                        [("id", "!=", rec.company_id.id)]
                    )
            else:
                rec.company_to_call_ids = False

    def _get_destinaries_email(self):
        missing_emails = [
            comp.name
            for comp in self.company_to_call_ids
            if not self.company_to_call_ids.requisition_intercompany_partner_ids
        ]
        if missing_emails:
            raise UserError(
                _("%s don't have contacts to send emails.")
                % (", ".join(missing_emails)),
            )
        return self.company_to_call_ids.requisition_intercompany_partner_ids.partner_id

    def action_call_for_proposal_send(self):
        for rec in self:
            template_id = rec.type_id.proposal_template_id.id
            lang = self.env.context.get("lang")
            template = self.env["mail.template"].browse(template_id)
            if template.lang:
                lang = template._render_lang(self.ids)[self.id]
            ctx = {
                "default_model": "purchase.requisition",
                "default_res_id": self.id,
                "default_use_template": bool(template_id),
                "default_template_id": template_id,
                "default_partner_ids": self._get_destinaries_email().ids,
                "default_composition_mode": "comment",
                "custom_layout": "mail.mail_notification_light",
                "force_email": True,
                "model_description": self.with_context(lang=lang).name,
            }

            return {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "mail.compose.message",
                "views": [(False, "form")],
                "view_id": False,
                "target": "new",
                "context": ctx,
            }

    @api.onchange("schedule_date")
    def _onchange_schedule_date(self):
        for line in self.line_ids:
            line.schedule_date = self.schedule_date

    @api.depends("requisition_proposal_ids")
    def _compute_requisition_proposal_count(self):
        for rec in self:
            rec.requisition_proposal_count = len(rec.requisition_proposal_ids)

    def show_requisition_proposal(self):
        views = [
            (
                self.env.ref(
                    "purchase_requisition_proposal.purchase_requisition_proposal_view_tree"
                ).id,
                "tree",
            ),
            (
                self.env.ref(
                    "purchase_requisition_proposal.purchase_requisition_proposal_view_form"
                ).id,
                "form",
            ),
        ]
        return {
            "name": "proposals",
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "view_mode": "tree,form",
            "res_model": "purchase.requisition.proposal",
            "target": "current",
            "domain": [("id", "in", self.requisition_proposal_ids.ids)],
            "views": views,
            "view_id": False,
        }

    def action_create_quotations(self):
        lines = self.requisition_proposal_ids.filtered(
            lambda x, s=self: x.qty_planned > 0
            and x not in s.purchase_ids.order_line.mapped("requirement_proposal_id")
        )
        partners = lines.mapped("partner_id")
        if lines:
            for partner in partners:
                fiscal_position = (
                    self.env["account.fiscal.position"]
                    .with_company(self.company_id)
                    .get_fiscal_position(partner.id)
                )
                proposals_lines = lines.filtered(lambda x, p=partner: x.partner_id == p)
                po_lines = []
                for line in proposals_lines:
                    taxes = fiscal_position.map_tax(
                        line.product_id.supplier_taxes_id.filtered(
                            lambda tax, c=self.company_id: tax.company_id == c
                        )
                    )
                    proposal_line = {
                        "product_id": line.product_id.id,
                        "price_unit": line.price_unit,
                        "product_qty": line.qty_planned,
                        "date_planned": line.date_planned,
                        "requirement_proposal_id": line.id,
                        "taxes_id": taxes.ids,
                    }
                    po_lines.append((0, 0, proposal_line))

                self.env["purchase.order"].create(
                    {
                        "requisition_id": self.id,
                        "partner_id": partner.id,
                        "fiscal_position_id": fiscal_position.id,
                        "order_line": po_lines,
                        "company_id": self.company_id.id,
                    }
                )

    def action_in_progress(self):
        super().action_in_progress()
        if self.type_id.exclusive == "proposals":
            self.name = self.env["ir.sequence"].next_by_code(
                "purchase.requisition.purchase.call"
            )
