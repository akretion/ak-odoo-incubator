# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    promotion_rule_ids = fields.Many2many(
        'sale.promotion.rule',
        string='Promotion rules',
        domain=[('rule_type', '!=', 'coupon')],
        readonly=True
    )

    coupon_promotion_rule_id = fields.Many2one(
        'sale.promotion.rule',
        string='Coupon promotion rule',
        domain=[('rule_type', '=', 'coupon')],
        readonly=True
    )
    coupon_code = fields.Char(
        related='coupon_promotion_rule_id.code',
        readonly=True,
        store=True
    )

    @api.multi
    def add_coupon(self, coupon_code):
        self.env['sale.promotion.rule'].apply_coupon(self, coupon_code)

    @api.multi
    def apply_promotion(self):
        self.env['sale.promotion.rule'].compute_promotions(self)
