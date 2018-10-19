# -*- coding: utf-8 -*-
# Copyright 2018 Acsone SA/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


line_restriction_amount_mapping = {
    'amount_total': 'price_total',
    'amount_untaxed': 'price_subtotal',
}


class SalePromotionRule(models.Model):

    _inherit = 'sale.promotion.rule'

    filter_id = fields.Many2one(
        "ir.filters",
        "Filter",
        help="Export only products matching with the filter domain",
        domain=[('is_assortment', '=', True)],
        context={
            'product_assortment': True,
            'default_is_assortment': 1},
    )

    def _get_promotion_rule_products(self):
        product_obj = self.env['product.product']
        if self.filter_id:
            domain = self.filter_id._get_eval_domain()
            return product_obj.search(domain)
        return product_obj.browse()

    def _get_promotions_valid_order_lines(self, order=False, line=False):
        promotion_product_ids = self._get_promotion_rule_products()
        if order:
            order_lines = order.order_line
        elif line:
            order_lines = line
        order_line_ids = order_lines.filtered(
            lambda order_line, product_ids=promotion_product_ids:
            order_line.product_id.id in product_ids.ids)
        return order_line_ids

    @api.model
    def _get_restrictions(self):
        res = super(SalePromotionRule, self)._get_restrictions()
        res.append('product_assortment')
        return res

    def _check_valid_product_assortment(self, order):
        if self.filter_id:
            order_lines = self._get_promotions_valid_order_lines(order=order)
            if not order_lines:
                return False

        return True

    def _is_promotion_valid_for_line(self, line):
        res = super(SalePromotionRule, self)
        if self.filter_id:
            order_lines = self._get_promotions_valid_order_lines(line=line)
            if not order_lines:
                return False
        return res

    def _get_line_amount_restriction_field(self):
        restriction_amount_field = line_restriction_amount_mapping.get(
            self.restriction_amount, False)
        if not restriction_amount_field:
            raise ValidationError(_('Restriction amount field unknown'))
        return restriction_amount_field

    def _check_valid_total_amount(self, order):
        if self.filter_id:
            precision = self.env['decimal.precision'].precision_get('Discount')
            restriction_amount = self._get_line_amount_restriction_field()

            line_ids = self._get_promotions_valid_order_lines(order=order)
            line_amount = sum([line[restriction_amount] for line in line_ids])

            return float_compare(
                self.minimal_amount,
                line_amount,
                precision_digits=precision) < 0
        return super(SalePromotionRule, self)._check_valid_total_amount(order)
