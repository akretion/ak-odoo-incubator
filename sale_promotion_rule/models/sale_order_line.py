# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_compare

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    promotion_rule_id = fields.Many2one(
        comodel_name='sale.promotion.rule',
        string='Promotion Rule')

    def _can_be_discounted(self, rule):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Discount')
        if self.discount and rule.use_best_discount:
            return float_compare(
                rule.discount_amount,
                self.discount,
                precision_digits=precision) > 0
        return not self.discount
