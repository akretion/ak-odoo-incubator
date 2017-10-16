# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class SalePromotionRule(models.Model):
    _inherit = 'sale.promotion.rule'

    apply_discount_on = fields.Selection(
        selection=[
            ('product', 'Product'),
            ('shipping', 'Shipping'),
            ('all', 'All'),
            ],
        required=True,
        default='product')
