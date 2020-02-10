# -*- coding: utf-8 -*-
# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class PartnerGenerateLdif(models.TransientModel):
    _name = 'wizard.partner.generate.ldif'
    _description = 'Partner Generate Ldif'

    partner_ids = fields.One2many('res.partner')

    def run(self)
        self.ensure_one()
        return self.partner_ids.generate_ldif()
