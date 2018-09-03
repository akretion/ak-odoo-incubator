# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    promotion_rule_id = fields.Many2one(
        'sale.promotion.rule',
        string='Promotion rule')

    @api.multi
    def clear_promotion_line(self):
        lines = self.mapped("order_line").filtered('promotion_rule_id')
        lines.write({'discount': 0, 'promotion_rule_id': False})

    @api.multi
    def clear_promotion(self):
        self.write({'promotion_rule_id': False})
        self.clear_promotion_line()

    @api.multi
    def add_coupon(self, coupon_code):
        rule = self.env['sale.promotion.rule'].search([
            ('code', '=ilike', coupon_code),
            ('rule_type', '=', 'coupon'),
            ])
        if not rule:
            raise UserError(
                _('Code number %s is invalid') % coupon_code)
        else:
            self.write({'promotion_rule_id': rule.id})
            self.apply_promotion()

    @api.multi
    def apply_promotion(self):
        self.clear_promotion_line()
        auto_rules = self.env['sale.promotion.rule'].search([
            ('rule_type', '=', 'auto'),
        ])
        order_no_rule = self.browse([])
        for order in self:
            if order.promotion_rule_id:
                if order.promotion_rule_id._is_promotion_valid(order):
                    order._apply_promotion_rule(order.promotion_rule_id)
                else:
                    raise UserError(
                        _('The rule cannot be applied on the sale order'))
            else:
                order_no_rule |= order
        for rule in auto_rules:
            order_to_apply = order_no_rule.filtered(
                lambda o, r=rule: r._is_promotion_valid(o))
            order_to_apply._apply_promotion_rule(rule)

    @api.multi
    def _apply_promotion_rule(self, rule):
        if rule.promo_type == 'discount':
            lines = self.mapped('order_line').filtered(
                lambda l, r=rule: l._can_be_discounted(r))
            lines.write({
                'discount': rule.discount_amount,
                'promotion_rule_id': rule.id,
            })
