# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import UserError


class DesktopCertificate(models.Model):
    _name = "desktop.certificate"
    _description = "Desktop Certificate"

    name = fields.Char(string="Nom")
    desktop_id = fields.Many2one(
        comodel_name="desktop",
        string="Poste",
    )
    active = fields.Boolean(default=True, string="Actif")
    revoked = fields.Boolean(string="Révoqué", default=False)
    expiration_date = fields.Datetime(string="Date d'expiration")
    sent_to_email = fields.Char(string="Destinataire mail")
    sent_to_phone = fields.Char(
        string="Destinataire SMS",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="desktop_id.company_id",
    )

    state = fields.Selection(
        selection=[
            ("obsolete", "Obsolète"),
            ("revoked", "Révoqué"),
            ("long", "> 3 mois"),
            ("medium", "< 3 mois"),
            ("short", "< 15 jours"),
        ],
        string="Etat du Certificat",
        compute="_compute_state",
        store=False,
    )

    def _compute_state(self):
        for rec in self:
            if rec.revoked or not rec.active:
                rec.state = "revoked"
            elif rec.expiration_date < datetime.now():
                rec.state = "obsolete"
            elif rec.expiration_date < datetime.now() + relativedelta(weeks=2):
                rec.state = "short"
            elif rec.expiration_date < datetime.now() + relativedelta(months=3):
                rec.state = "medium"
            else:
                rec.state = "long"


    def write(self, vals):
        if "active" in vals:
            if vals["active"] and self.expiration_date > datetime.now() and not self.revoked:
                mpki_api = self.desktop_id._get_mpki_api()
                res = requests.delete(
                    mpki_api["url"],
                    auth=(mpki_api["user"], mpki_api["password"]),
                    params={"serial": self.serial},
                )
                # Archive if certificate is revoked or not found (already revoked)
                if res.status_code == requests.codes.ok or res.status_code == 404:
                    self.revoked = True
                else:
                    try:
                        raise UserError(json.dumps(res.json(), indent=4))
                    except ValueError:
                        raise UserError(res.text)
            elif not vals["active"]:
                raise UserError(
                    _(
                        "Vous ne pouvez pas désarchiver un certificat, "
                        "veuillez en générer un nouveau."
                    )
                )
            else:
                raise UserError(
                    _(
                        "Vous ne pouvez pas activer un certificat déjà révoqué"
                        " ou obsolète."
                    )
                )
        return super().write()


