# -*- coding: utf-8 -*-
# Copyright 2018 Acsone Sa/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.addons.sale_promotion_rule.tests.test_promotion import \
    AbstractCommonPromotionCase


class TestPromotionRuleAssortment(TransactionCase,
                                  AbstractCommonPromotionCase):

    def setUp(self):
        super(TestPromotionRuleAssortment, self).setUp()
        self.set_up('sale.sale_order_3')
        self.line_consu = self.env.ref('sale.sale_order_line_7')
        self.line_service = self.env.ref('sale.sale_order_line_6')
        ir_filter = self.env.ref(
            'sale_promotion_rule_assortment.promotion_assortment1')
        # restrict rule to consumable products
        self.promotion_rule_auto.filter_id = ir_filter.id

    def test_promotion_rule_assortment(self):
        """
        Test auto appliance of a automatic promotion rule on a reduced of
        products.
        - it should be applied on consumable products
        - it should not be applied on service products
        :return:
        """
        self.sale.apply_promotions()

        self.check_discount_rule_set(self.line_consu, self.promotion_rule_auto)
        with self.assertRaises(AssertionError):
            self.check_discount_rule_set(self.line_service,
                                         self.promotion_rule_auto)

    def test_promotion_rule_assortment_minimum_not_reached(self):
        """
        Test auto appliance of a automatic promotion rule on a reduced of
        products.
        - it should be applied on consumable products only if minimum amount
        is reached
        - it should not be applied on service products
        :return:
        """
        self.promotion_rule_auto.minimal_amount = 80

        self.sale.apply_promotions()

        with self.assertRaises(AssertionError):
            self.check_discount_rule_set(self.line_consu,
                                         self.promotion_rule_auto)
        with self.assertRaises(AssertionError):
            self.check_discount_rule_set(self.line_service,
                                         self.promotion_rule_auto)

        self.line_consu.product_uom_qty = 2

        self.sale.apply_promotions()

        self.check_discount_rule_set(self.line_consu,
                                     self.promotion_rule_auto)
