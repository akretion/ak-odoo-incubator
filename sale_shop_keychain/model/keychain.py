# -*- coding: utf-8 -*-

from openerp import fields, models


class KeychainAccount(models.Model):
    _inherit = 'keychain.account'

    sale_shop_ids = fields.Many2many(
        comodel_name='sale.shop', string="Shop ids")
