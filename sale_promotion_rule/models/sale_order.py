# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    promotion_rule_id = fields.Many2one(
        'sale.promotion.rule',
        string='Promotion rule')

    @api.multi
    def clear_promotion_line(self):
        for order in self:
            for line in order.order_line:
                if line.promotion_rule_id:
                    line.write({'discount': 0, 'promotion_rule_id': False})

    @api.multi
    def add_coupon(self, coupon_code):
        self.ensure_one()
        rule = self.env['sale.promotion.rule'].search([
            ('code', '=', coupon_code),
            ('rule_type', '=', 'coupon'),
            ])
        if not rule:
            raise UserError(
                _('Code number %s is invalid' % coupon_code))
        else:
            self.promotion_rule_id = rule
            self.apply_promotion()

    @api.multi
    def apply_promotion(self):
        for order in self:
            order.clear_promotion_line()
            if order.promotion_rule_id:
                if order.promotion_rule_id._is_promotion_valid(order):
                    order._apply_promotion_rule()
                else:
                    raise UserError(
                        _('The rule cannot be applied on the sale order'))

    def _apply_promotion_rule(self):
        self.ensure_one()
        rule = self.promotion_rule_id
        if rule.promo_type.startswith('discount'):
            for line in self.order_line:
                if line._can_be_discounted(rule):
                    line.write({
                        'discount': rule.discount_amount,
                        'promotion_rule_id': rule.id,
                        })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    promotion_rule_id = fields.Many2one(
        comodel_name='sale.promotion.rule',
        string='Promotion Rule')

    def _can_be_discounted(self, rule):
        self.ensure_one()
        key = rule.promo_type.replace('discount_on_', '')
        return not self.discount and (
            key == 'all'
            or (key == 'shipping' and self.is_delivery)
            or (key == 'product' and not self.is_delivery))
