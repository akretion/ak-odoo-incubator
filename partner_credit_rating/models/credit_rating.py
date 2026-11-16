# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError

RISKS = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
]


class CreditRating(models.Model):
    """Credit rating of a commercial partner.

    Provider modules implement, for a provider key `xxx`:

    - `_search_xxx(criteria)` (model method): return a list of dict with keys
      ref, name, street, zip, city, country_code, vat, registry
    - `_fetch_xxx()`: return a dict with keys
      code, label, score (0 worst - 100 best), risk (see RISKS)
    """

    _name = "credit.rating"
    _description = "Credit Rating"
    _rec_name = "partner_id"
    _order = "date desc, id desc"

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        index=True,
        ondelete="cascade",
        domain=[("is_company", "=", True)],
    )
    provider = fields.Selection(
        selection="_selection_provider", required=True, readonly=True
    )
    ref = fields.Char(
        string="Reference",
        index="btree_not_null",
        help="Company identifier at the credit rating provider",
    )
    code = fields.Char(string="Rating", readonly=True, help="Raw provider rating")
    label = fields.Char(readonly=True)
    score = fields.Integer(
        readonly=True, help="Normalized score: 0 (worst) to 100 (best)"
    )
    risk = fields.Selection(RISKS, string="Credit Risk", readonly=True)
    date = fields.Datetime(readonly=True)
    monitor = fields.Boolean(
        help="Refresh the rating periodically with the scheduled action"
    )

    _partner_uniq = models.Constraint(
        "unique(partner_id)", "A company can only have one credit rating."
    )

    @api.model
    def _selection_provider(self):
        return []

    def _call(self, method, *args, provider=None):
        """Dispatch to the provider implementation: the rating one by default"""
        provider = provider or self.provider
        if not provider:
            raise UserError(self.env._("No credit rating provider defined."))
        return getattr(self, f"_{method}_{provider}")(*args)

    def action_refresh(self):
        for rating in self:
            if not rating.ref:
                raise UserError(
                    self.env._(
                        "%s: identify the company at the rating provider first.",
                        rating.partner_id.display_name,
                    )
                )
            old_code, old_risk = rating.code, rating.risk
            vals = rating._call("fetch")
            rating.write(
                {
                    "code": vals.get("code"),
                    "label": vals.get("label"),
                    "score": vals.get("score"),
                    "risk": vals.get("risk"),
                    "date": fields.Datetime.now(),
                }
            )
            if rating.code != old_code:
                rating.partner_id.message_post(
                    body=self.env._(
                        "Credit rating: %(old)s → %(new)s (%(label)s)",
                        old=old_code or "-",
                        new=rating.code or "-",
                        label=rating.label or "",
                    )
                )
            rating._rating_changed(old_risk)
        return True

    def _rating_changed(self, old_risk):
        """Hook called after a rating refresh, e.g. to block sales"""

    @api.model
    def _cron_monitor(self, limit=200):
        ratings = self.search(
            [("monitor", "=", True), ("ref", "!=", False)],
            limit=limit,
            order="date ASC nulls first, id",
        )
        for rating in ratings:
            try:
                with self.env.cr.savepoint():
                    rating.action_refresh()
            except UserError as e:
                rating.partner_id.message_post(
                    body=self.env._("Credit rating refresh failed: %s", e)
                )
