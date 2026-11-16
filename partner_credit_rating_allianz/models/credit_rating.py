# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: David Beal <david.beal@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

import requests

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import LazyTranslate

_lt = LazyTranslate(__name__)

TIMEOUT = 30

GRADES = {
    "01": _lt("Exceptional"),
    "02": _lt("Strong"),
    "03": _lt("Good"),
    "04": _lt("Above average"),
    "05": _lt("Average"),
    "06": _lt("Under watch"),
    "07": _lt("Weak"),
    "08": _lt("High risk"),
    "09": _lt("Uninsurable"),
    "10": _lt("Defaulted"),
    "NA": _lt("Not applicable"),
}

# Allianz idTypeCode used for the partner Company ID (EN identifier), by country
REGISTRY_TYPES = {"FR": "SIREN"}


class CreditRating(models.Model):
    _inherit = "credit.rating"

    @api.model
    def _selection_provider(self):
        return super()._selection_provider() + [("allianz", "Allianz Trade")]

    @api.model
    def _allianz_param(self, key):
        icp = self.env["ir.config_parameter"].sudo()
        return icp.get_str(f"allianz_trade.{key}").strip()

    @api.model
    def _allianz_url(self, service):
        env = self._allianz_param("env") or "uat"
        url = self._allianz_param(f"{service}_base_{env}")
        if not url:
            raise UserError(
                _(
                    "Allianz Trade: missing %(service)s URL (%(env)s).",
                    service=service,
                    env=env,
                )
            )
        return url.rstrip("/")

    @api.model
    def _allianz_request(self, method, url, auth=True, **kwargs):
        headers = {"Accept": "application/json"}
        if auth:
            headers["Authorization"] = f"Bearer {self._allianz_token()}"
            headers["x-api-key"] = self._allianz_param("api_key")
        try:
            resp = requests.request(
                method, url, headers=headers, timeout=TIMEOUT, **kwargs
            )
        except requests.RequestException as e:
            raise UserError(_("Allianz Trade network error: %s", e)) from e
        try:
            data = resp.json() if resp.text else {}
        except ValueError:
            data = {"raw": resp.text}
        if resp.status_code >= 400:
            raise UserError(
                _(
                    "Allianz Trade error %(status)s:\n%(data)s",
                    status=resp.status_code,
                    data=data,
                )
            )
        return data

    @api.model
    def _allianz_token(self, force=False):
        icp = self.env["ir.config_parameter"].sudo()
        now = int(time.time())
        token = icp.get_str("allianz_trade.cached_token")
        expire = icp.get_int("allianz_trade.cached_token_exp")
        if token and now < expire - 30 and not force:
            return token
        api_key = self._allianz_param("api_key")
        if not api_key:
            raise UserError(_("Allianz Trade: missing API key."))
        data = self._allianz_request(
            "POST",
            f"{self._allianz_url('idp')}/oauth2/authorize",
            auth=False,
            json={"apiKey": api_key},
        )
        token = data.get("access_token")
        if not token:
            raise UserError(_("Allianz Trade: no access token in %s", data))
        icp.set_str("allianz_trade.cached_token", token)
        icp.set_int(
            "allianz_trade.cached_token_exp",
            now + int(data.get("expires_in") or 3600),
        )
        return token

    @api.model
    def _allianz_identifiers(self, criteria):
        """Return (idTypeCode, idValue) to search for, most specific first"""
        country, registry, vat = (
            criteria["country_code"],
            criteria["registry"],
            criteria["vat"],
        )
        if country == "FR":
            # SIRET -> SIREN, or SIREN from VAT: FR + 2 key digits + SIREN
            registry = registry[:9] or (vat[4:13] if vat.startswith("FR") else "")
        ids = []
        if registry and country in REGISTRY_TYPES:
            ids.append((REGISTRY_TYPES[country], registry))
        if vat:
            ids.append(("VAT", vat))
        return ids

    @api.model
    def _search_allianz(self, criteria):
        if not criteria["country_code"]:
            raise UserError(_("Allianz Trade search requires a country."))
        ids = self._allianz_identifiers(criteria)
        if not ids:
            raise UserError(
                _("Allianz Trade search requires a Company ID or a Tax ID.")
            )
        url = f"{self._allianz_url('companysearch')}/companies/advancedSearch"
        for id_type, value in ids:
            data = self._allianz_request(
                "POST",
                url,
                json={
                    "idTypeCode": id_type,
                    "idValue": value,
                    "countryCode": criteria["country_code"],
                },
            )
            results = [
                self._allianz_result(res.get("company") or {})
                for res in data.get("results") or []
            ]
            results = [res for res in results if res["ref"]]
            if results:
                return results
        return []

    @api.model
    def _allianz_result(self, company):
        address = company.get("address") or {}
        ids = {
            ident.get("idTypeCode"): ident.get("idValue")
            for ident in company.get("companyIdentifiers") or []
        }
        street = " ".join(
            filter(None, [address.get("streetNumber"), address.get("streetName")])
        )
        return {
            "ref": company.get("companyId"),
            "name": (company.get("legalData") or {}).get("companyName"),
            "street": street,
            "zip": next(
                (pc.get("postCodeValue") for pc in address.get("postCodes") or []),
                False,
            ),
            "city": address.get("town"),
            "country_code": address.get("countryCode"),
            "registry": ids.get("SIREN") or ids.get("SIRET"),
            "vat": ids.get("VAT"),
        }

    def _fetch_allianz(self):
        self.ensure_one()
        unit = self._allianz_param("business_unit_code")
        policy = self._allianz_param("policy_id")
        if not unit or not policy:
            raise UserError(_("Allianz Trade: missing Business Unit Code or Policy."))
        data = self._allianz_request(
            "POST",
            f"{self._allianz_url('gradecheck')}/monitoredGrades/search",
            json={
                "companyIds": [self.ref],
                "policies": [{"businessUnitCode": unit, "policyId": policy}],
            },
        )
        if isinstance(data, dict):
            data = data.get("results") or data.get("items") or []
        if not data:
            raise UserError(_("Allianz Trade: no grade for %s", self.ref))
        code = (data[0].get("monitoredGradeCode") or "").strip()
        return {"code": code, "label": str(GRADES.get(code, ""))} | (
            self._allianz_score(code)
        )

    @api.model
    def _allianz_score(self, code):
        """Allianz grade: 01 (best) to 10 (default)"""
        grade = int(code) if code.isdigit() else 0
        if not 1 <= grade <= 10:
            return {"score": 0, "risk": False}
        if grade <= 3:
            risk = "low"
        elif grade <= 6:
            risk = "medium"
        elif grade == 7:
            risk = "high"
        else:
            risk = "critical"
        return {"score": (10 - grade) * 100 // 9, "risk": risk}
