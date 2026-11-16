# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command as cmd
from odoo import fields, models
from odoo.exceptions import UserError


class CreditRatingSearch(models.TransientModel):
    _name = "credit.rating.search"
    _description = "Credit Rating Company Search"

    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")
    provider = fields.Selection(
        selection=lambda self: self.env["credit.rating"]._selection_provider(),
        required=True,
        default=lambda self: self.env.company.rating_provider,
    )
    name = fields.Char()
    vat = fields.Char(string="Tax ID")
    registry = fields.Char(string="Company ID")
    country_id = fields.Many2one("res.country")
    zip = fields.Char()
    city = fields.Char()
    line_ids = fields.One2many("credit.rating.search.line", "wizard_id")

    def _criteria(self):
        return {
            "name": self.name or "",
            "vat": (self.vat or "").replace(" ", "").upper(),
            "registry": (self.registry or "").replace(" ", ""),
            "country_code": self.country_id.code or "",
            "zip": self.zip or "",
            "city": self.city or "",
        }

    def action_search(self):
        self.ensure_one()
        results = self.env["credit.rating"]._call(
            "search", self._criteria(), provider=self.provider
        )
        self.line_ids = [cmd.clear()] + [cmd.create(vals) for vals in results]
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Credit Rating Search"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }


class CreditRatingSearchLine(models.TransientModel):
    _name = "credit.rating.search.line"
    _description = "Credit Rating Company Search Result"

    wizard_id = fields.Many2one(
        "credit.rating.search", required=True, ondelete="cascade"
    )
    ref = fields.Char(string="Reference", required=True)
    name = fields.Char()
    street = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    country_code = fields.Char(string="Country")
    vat = fields.Char(string="Tax ID")
    registry = fields.Char(string="Company ID")

    def action_select(self):
        self.ensure_one()
        partner = self.wizard_id.partner_id
        rating = partner._get_credit_rating(self.wizard_id.provider)
        rating.ref = self.ref
        try:
            with self.env.cr.savepoint():
                rating.action_refresh()
        except UserError as e:
            # keep the reference even if the rating is not available yet
            partner.message_post(body=self.env._("Credit rating refresh failed: %s", e))
        return {"type": "ir.actions.act_window_close"}
