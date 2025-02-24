# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

import json
from datetime import datetime

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Desktop(models.Model):
    _name = "desktop"
    _inherit = ["mail.thread"]
    _description = "Desktop"

    name = fields.Char(string="Nom")
    address_id = fields.Many2one(
        comodel_name="res.partner", string="Lieu", required=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Société",
        default=lambda self: self.env.user.company_id,
    )
    certificate_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Certificats envoyés à",
        domain=[("user_ids", "!=", False)],
        default=lambda self: self.env.user.partner_id,
    )
    certificate_email = fields.Char(
        string="Certificat envoyé à", related="certificate_partner_id.email"
    )
    certificate_phone = fields.Char(
        string="Mot de passe du certificat envoyé à",
        related="certificate_partner_id.mobile",
    )

    certificate_ids = fields.One2many(
        comodel_name="desktop.certificate",
        inverse_name="desktop_id",
        string="Certificats",
    )
    certificate_state = fields.Selection(
        selection=[
            ("1_short", "< 15 jours"),
            ("2_medium", "< 3 mois"),
            ("3_long", "> 3 mois"),
            ("4_revoked", "Révoqué"),
            ("5_obsolete", "Obsolète"),
            ("none", "Aucun certificat"),
        ],
        string="Etat Certificats",
        compute="_compute_valid_certificate_state",
        store=True,
    )

    certificate_min_exp_date = fields.Date(
        string="Date d'expiration",
        compute="_compute_certificate_min_exp_date",
    )

    valid_certificate_count = fields.Integer(
        compute="_compute_valid_certificate_count", string="Certificats Valides"
    )

    def _compute_certificate_min_exp_date(self):
        for rec in self:
            rec.certificate_min_exp_date = None
            certifs = rec.certificate_ids
            if certifs:
                current_datetime = datetime.now()
                valid_datetime_list = [
                    certif.expiration_date
                    for certif in certifs
                    if certif.expiration_date >= current_datetime
                    and not certif.revoked
                    and certif.active
                ]
                if valid_datetime_list:
                    rec.certificate_min_exp_date = max(valid_datetime_list).date()

    def _compute_valid_certificate_state(self):
        for rec in self:
            certif_states = rec.certificate_ids.mapped("state")
            if certif_states:
                if "short" in certif_states:
                    rec.certificate_state = "1_short"
                elif "medium" in certif_states:
                    rec.certificate_state = "2_medium"
                elif "long" in certif_states:
                    rec.certificate_state = "3_long"
                elif "revoked" in certif_states:
                    rec.certificate_state = "4_revoked"
                else:
                    rec.certificate_state = "5_obsolete"
            else:
                rec.certificate_state = "none"

    def cron_send_email_certificate_expiration(self):
        certifs = self.env["maintenance.certificate"].search([])
        certifs._compute_valid_certificate_state()
        short_certifs = certifs.filtered(lambda x: x.state == "short")
        if short_certifs:
            email_template = self.env.ref("infra.mail_certificate_expiration")
            self.with_context(
                certifs_ids=short_certifs.equipment_id
            ).message_post_with_template(email_template.id)

    @api.depends("certificate_ids")
    def _compute_valid_certificate_count(self):
        for record in self:
            record.valid_certificate_count = len(
                record.certificate_ids.filtered(
                    lambda c: not c.revoked and c.expiration_date > datetime.now()
                )
            )

    def _get_mpki_api(self):
        ir_config_model = self.env["ir.config_parameter"].sudo()
        mpki_api = {}
        mpki_api["url"] = ir_config_model.get_param("mpki_api_url")
        mpki_api["user"] = ir_config_model.get_param("mpki_api_user")
        mpki_api["password"] = ir_config_model.get_param("mpki_api_password")
        return mpki_api

    def generate_certificate(self):
        mpki_api = self._get_mpki_api()
        for record in self:
            partner = record.certificate_partner_id
            if not partner.email:
                raise UserError(_("L'email du destinataire est vide"))
            if not partner.mobile:
                raise UserError(_("Le mobile du destinataire est vide"))
            address = record.address_id
            params = {
                "certificate": {
                    "name": record.name,
                },
                "partner": {
                    "name": partner.display_name,
                    "phone": partner.mobile,
                    "email": partner.email,
                },
                "location": {
                    "name": address.name,
                    "company": self.company_id.name,
                    "city": address.city,
                    "zipcode": address.zip,
                    "country": address.country_id.code,
                },
            }
            res = requests.post(
                mpki_api["url"],
                auth=(mpki_api["user"], mpki_api["password"]),
                json=params,
            )
            if res.status_code == requests.codes.ok:
                res_dict = res.json()
                self.env["desktop.certificate"].create(
                    {
                        "revoked": not res_dict["valid"],
                        "name": res_dict["name"],
                        "expiration_date": datetime.fromisoformat(
                            res_dict["valid_until"]
                        ),
                        "desktop_id": record.id,
                        "sent_to_email": record.certificate_email,
                        "sent_to_phone": record.certificate_phone,
                    }
                )
            else:
                try:
                    raise UserError(json.dumps(res.json(), indent=4))
                except ValueError:
                    raise UserError(res.text)
        return None

    def unlink(self):
        desktops = self.mapped("desktop_id")
        super().unlink()
        desktops.unlink()
        return True
