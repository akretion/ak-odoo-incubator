# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _can_be_discounted(self, rule):
        self.ensure_one()
        res = super(SaleOrderLine, self)._can_be_discounted(rule)
        return res and (
            rule.apply_discount_on == 'all' or
            (rule.apply_discount_on == 'shipping' and self.is_delivery) or
            (rule.apply_discount_on == 'product' and not self.is_delivery))
