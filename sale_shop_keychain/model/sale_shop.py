# -*- coding: utf-8 -*-

from openerp import fields, models


class SaleShop(models.Model):
    _inherit = 'sale.shop'

    keychain_account_ids = fields.Many2many(
        comodel_name='keychain.account', string="Allow accounts")
