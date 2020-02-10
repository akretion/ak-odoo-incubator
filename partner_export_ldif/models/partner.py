# -*- coding: utf-8 -*-
# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ldap
import tempfile

from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    
    ldap_update_record = fields.Boolean("To update on LDAP")
    ldap_create_record = fields.Boolean("To create on LDAP")

    @api.multi
    def generate_ldif(self):
        entries = []
        dn = "CN=LDAP Search,CN=Users,DC=lacimade,DC=global"
        with tempfile.SpooledTemporaryFile(mode="w", encoding="utf-8") as res:
            writer = ldap.ldif.LDIFWriter(res)
            for record in self.filtered(lambda x: x.ldap_create_record):
                writer.unparse(dn, record.generate_create_entry())
            for record in self.filtered(lambda x: x.ldap_update_record):
                writer.unparse(dn, record.generate_update_entry())
            return res

    @api.multi
    def generate_create_entry(self):
        self.ensure_one()
        return {"objectClass": ["person"], "cn": [self.email]}

    @api.multi
    def generate_update_entry(self):
        self.ensure_one()
        return {"objectClass": ["person"], "cn": [self.email]}
