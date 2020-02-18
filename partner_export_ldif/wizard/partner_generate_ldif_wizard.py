# -*- coding: utf-8 -*-
# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PartnerGenerateLdif(models.TransientModel):
    _name = "wizard.partner.generate.ldif"
    _description = "Partner Generate Ldif"

    @api.model
    def _default_line_ids(self):
        if self._context.get(
            "active_model"
        ) == "res.partner" and self._context.get("active_ids"):
            partner_ids = self._context["active_ids"]
            line_changes = []
            for partner_id in partner_ids:
                line_changes.append((0, 0, {"partner_id": partner_id}))
            return line_changes

    line_ids = fields.One2many("wizard.partner.generate.ldif.line", "wizard_id", default=_default_line_ids)

    def run(self):
        self.ensure_one()
        partners = self.line_ids.mapped("partner_id")
        return partners.generate_ldif()

    def confirm_done(self):
        self.ensure_one()
        partners = self.line_ids.mapped("partner_id")
        return partners.write({"ldap_create_record": False, "ldap_update_record": False})

class PartnerGenerateLdifLine(models.TransientModel):
    _name = "wizard.partner.generate.ldif.line"
    _description = "Partner Generate Ldif Line"

    wizard_id = fields.Many2one(
        'wizard.partner.generate.ldif',
        'Wizard')
    partner_id = fields.Many2one(
        'res.partner',
        'Partner')
    ldap_update_record = fields.Boolean(related="partner_id.ldap_update_record")
    ldap_create_record = fields.Boolean(related="partner_id.ldap_create_record")
