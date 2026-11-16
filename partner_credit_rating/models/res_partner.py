# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # no column on res_partner: rating is stored on the commercial partner side
    credit_rating_ids = fields.One2many(
        "credit.rating", "partner_id", string="Credit Ratings"
    )
    credit_rating_id = fields.Many2one(
        "credit.rating",
        compute="_compute_credit_rating_id",
        search="_search_credit_rating_id",
    )
    credit_risk = fields.Selection(related="credit_rating_id.risk")
    credit_rating_code = fields.Char(
        related="credit_rating_id.code", string="Credit Rating Code"
    )

    @api.depends("commercial_partner_id.credit_rating_ids")
    def _compute_credit_rating_id(self):
        for partner in self:
            partner.credit_rating_id = partner._get_main_credit_rating()

    def _get_main_credit_rating(self):
        """Rating shown on the partner, override to choose among several"""
        self.ensure_one()
        return self.commercial_partner_id.credit_rating_ids[:1]

    def _get_credit_rating(self, provider):
        """Return the rating of the commercial partner for this provider,
        created if needed. Only one rating per company: a provider change
        reuses the existing rating."""
        self.ensure_one()
        partner = self.commercial_partner_id
        rating = partner.credit_rating_ids.filtered(lambda r: r.provider == provider)
        if not rating and partner.credit_rating_ids:
            rating = partner.credit_rating_ids[:1]
            rating.write(
                {
                    "provider": provider,
                    "ref": False,
                    "code": False,
                    "label": False,
                    "score": 0,
                    "risk": False,
                    "date": False,
                }
            )
        return rating[:1] or self.env["credit.rating"].create(
            {"partner_id": partner.id, "provider": provider}
        )

    def _search_credit_rating_id(self, operator, value):
        return [("commercial_partner_id.credit_rating_ids", operator, value)]

    def _get_rating_registry(self):
        """Company ID (former company_registry field): the enterprise number
        (EN category) with the lowest sequence, e.g. SIRET before SIREN"""
        self.ensure_one()
        vals = self._pick_preferred_identifier(
            self.additional_identifiers or {},
            filter_func=lambda key, value, meta: meta.get("category") == "EN",
            sort_key=lambda key, value, meta: meta.get("sequence", 100),
        )
        return vals.get("value") or False

    def action_rating_search(self):
        self.ensure_one()
        if not self.env.company.rating_provider:
            raise UserError(
                self.env._("No credit rating provider configured on the company.")
            )
        partner = self.commercial_partner_id
        wizard = self.env["credit.rating.search"].create(
            {
                "partner_id": partner.id,
                "name": partner.name,
                "vat": partner.vat,
                "registry": partner._get_rating_registry(),
                "country_id": partner.country_id.id,
                "zip": partner.zip,
                "city": partner.city,
            }
        )
        return wizard.action_search()

    def action_rating_open(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "credit.rating",
            "res_id": self.credit_rating_id.id,
            "view_mode": "form",
        }
