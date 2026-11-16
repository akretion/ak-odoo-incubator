# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

TIMEOUT = 30
# token lifetime is 1 hour
TOKEN_TTL = 3300

URLS = {
    "sandbox": "https://connect.sandbox.creditsafe.com/v1",
    "prod": "https://connect.creditsafe.com/v1",
}

# Creditsafe international score: A 71-100, B 51-70, C 30-50, D 1-29, E not rated
RISKS = {"A": "low", "B": "medium", "C": "high", "D": "critical"}


class CreditRating(models.Model):
    _inherit = "credit.rating"

    credit_limit = fields.Monetary(
        currency_field="limit_currency_id",
        readonly=True,
        help="Credit limit advised by the provider",
    )
    limit_currency_id = fields.Many2one("res.currency", readonly=True)

    @api.model
    def _selection_provider(self):
        return super()._selection_provider() + [("creditsafe", "Creditsafe")]

    @api.model
    def _creditsafe_param(self, key):
        icp = self.env["ir.config_parameter"].sudo()
        return icp.get_str(f"creditsafe.{key}").strip()

    @api.model
    def _creditsafe_url(self):
        return URLS[self._creditsafe_param("env") or "sandbox"]

    @api.model
    def _creditsafe_token(self, force=False):
        icp = self.env["ir.config_parameter"].sudo()
        now = int(time.time())
        token = icp.get_str("creditsafe.cached_token")
        if token and now < icp.get_int("creditsafe.cached_token_exp") and not force:
            return token
        username = self._creditsafe_param("username")
        password = self._creditsafe_param("password")
        if not username or not password:
            raise UserError(self.env._("Creditsafe: missing username or password."))
        data = self._creditsafe_request(
            "POST",
            "/authenticate",
            auth=False,
            json={"username": username, "password": password},
        )
        token = data.get("token")
        if not token:
            raise UserError(self.env._("Creditsafe: no token in %s", data))
        icp.set_str("creditsafe.cached_token", token)
        icp.set_int("creditsafe.cached_token_exp", now + TOKEN_TTL)
        return token

    @api.model
    def _creditsafe_request(self, method, path, auth=True, retry=True, **kwargs):
        headers = {"Accept": "application/json"}
        if auth:
            headers["Authorization"] = f"Bearer {self._creditsafe_token()}"
        try:
            resp = requests.request(
                method,
                f"{self._creditsafe_url()}{path}",
                headers=headers,
                timeout=TIMEOUT,
                **kwargs,
            )
        except requests.RequestException as e:
            raise UserError(self.env._("Creditsafe network error: %s", e)) from e
        if auth and retry and resp.status_code == 401:
            # cached token revoked or expired earlier than expected
            self._creditsafe_token(force=True)
            return self._creditsafe_request(
                method, path, auth=auth, retry=False, **kwargs
            )
        try:
            data = resp.json() if resp.text else {}
        except ValueError:
            data = {"raw": resp.text}
        if resp.status_code >= 400:
            raise UserError(
                self.env._(
                    "Creditsafe error %(status)s:\n%(data)s",
                    status=resp.status_code,
                    data=data,
                )
            )
        return data

    @api.model
    def _creditsafe_queries(self, criteria):
        """Search parameters to try, most specific first: Creditsafe only
        accepts some combinations of criteria"""
        queries = []
        if criteria["registry"]:
            queries.append({"regNo": criteria["registry"]})
        if criteria["vat"]:
            queries.append({"vatNo": criteria["vat"]})
        if criteria["name"]:
            query = {"name": criteria["name"]}
            if criteria["city"]:
                query["city"] = criteria["city"]
            queries.append(query)
        return queries

    @api.model
    def _search_creditsafe(self, criteria):
        if not criteria["country_code"]:
            raise UserError(self.env._("Creditsafe search requires a country."))
        queries = self._creditsafe_queries(criteria)
        if not queries:
            raise UserError(
                self.env._("Creditsafe search requires a Company ID, Tax ID or name.")
            )
        for query in queries:
            data = self._creditsafe_request(
                "GET",
                "/companies",
                params={
                    "countries": criteria["country_code"],
                    "pageSize": 50,
                    **query,
                },
            )
            results = [
                self._creditsafe_result(company)
                for company in data.get("companies") or []
            ]
            results = [res for res in results if res["ref"]]
            if results:
                return results
        return []

    @api.model
    def _creditsafe_result(self, company):
        address = company.get("address") or {}
        street = address.get("street") or ""
        if address.get("houseNo"):
            street = f"{address['houseNo']} {street}"
        return {
            "ref": company.get("id"),
            "name": company.get("name"),
            "street": street,
            "zip": address.get("postCode"),
            "city": address.get("city"),
            "country_code": company.get("country"),
            "registry": company.get("regNo"),
            "vat": (company.get("vatNo") or [False])[0],
        }

    def _creditsafe_report(self):
        self.ensure_one()
        report = self._creditsafe_request(
            "GET", f"/companies/{self.ref}", params={"language": "en"}
        ).get("report", {})
        rating = report.get("creditScore", {}).get("currentCreditRating", {})
        branches = report.get("additionalInformation", {}).get("branches") or []
        if rating.get("commonDescription") == "Not Scored" and branches:
            # rating is carried by the first branch (e.g. head office)
            report = self._creditsafe_request(
                "GET",
                f"/companies/{branches[0]['id']}",
                params={"language": "en"},
            ).get("report", {})
        return report

    def _fetch_creditsafe(self):
        self.ensure_one()
        report = self._creditsafe_report()
        rating = report.get("creditScore", {}).get("currentCreditRating", {})
        if not rating:
            raise UserError(self.env._("Creditsafe: no rating for %s", self.ref))
        limit = rating.get("creditLimit") or {}
        currency = (
            self.env["res.currency"]
            .with_context(active_test=False)
            .search([("name", "=", limit.get("currency"))], limit=1)
        )
        # extra values: not handled by the base module
        self.write(
            {
                "credit_limit": float(limit.get("value") or 0),
                "limit_currency_id": currency.id,
            }
        )
        common = rating.get("commonValue") or ""
        value = rating.get("providerValue") or {}
        return {
            "code": value.get("value") or common,
            "label": " - ".join(
                filter(None, [common, rating.get("commonDescription")])
            ),
            "score": self._creditsafe_score(value),
            "risk": RISKS.get(common, False),
        }

    @api.model
    def _creditsafe_score(self, value):
        """Normalize the local provider score with its min / max values"""
        try:
            score = float(value["value"])
            low = float(value.get("minValue") or 0)
            high = float(value.get("maxValue") or 100)
        except (KeyError, TypeError, ValueError):
            return 0
        if high <= low:
            return 0
        return round(max(0, min(100, (score - low) * 100 / (high - low))))
