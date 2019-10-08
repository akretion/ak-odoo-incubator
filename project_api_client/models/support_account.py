# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SupportAccount(models.Model):
    _name = "support.account"
    _description = "Support account"

    name = fields.Char()
    url = fields.Char()
    api_key = fields.Char()
    company_id = fields.Many2one(comodel_name='res.company')

    def retrieve(self):
        account = self.search([('company_id', '=', self.env.user.company_id.id)])
        if not account:
            account = self.search([('company_id', '=', False)])
        return account
