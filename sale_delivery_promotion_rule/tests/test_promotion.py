# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.addons.sale_promotion_rule.tests.test_promotion import (
    AbstractCommonPromotionCase)


class AbstractPromotionDeliveryCase(AbstractCommonPromotionCase):

    def set_up(self):
        super(AbstractPromotionDeliveryCase, self).set_up()
        self.sale.carrier_id = self.env.ref('delivery.normal_delivery_carrier')
        self.sale.delivery_set()
        self.promotion_rule = self.env.ref('sale_promotion_rule.rule_1')

    def test_add_valid_discount_code_for_delivery(self):
        self.promotion_rule.apply_discount_on = 'shipping'
        self.add_coupon_code('ELDONGHUT')
        for line in self.sale.order_line[0:-1]:
            self.assertEqual(line.discount, 0)
            self.assertEqual(line.promotion_rule_id.id, False)
        delivery_line = self.sale.order_line[-1]
        self.check_discount_rule_set(delivery_line, self.promotion_rule)

    def test_add_valid_discount_code_for_all_line(self):
        self.promotion_rule.apply_discount_on = 'all'
        self.add_coupon_code('ELDONGHUT')
        for line in self.sale.order_line[0:-1]:
            self.check_discount_rule_set(line, self.promotion_rule)

    def test_add_valid_discount_code_for_product(self):
        self.add_coupon_code('ELDONGHUT')
        for line in self.sale.order_line[0:-1]:
            self.check_discount_rule_set(line, self.promotion_rule)
        delivery_line = self.sale.order_line[-1]
        self.assertEqual(delivery_line.discount, 0)
        self.assertEqual(delivery_line.promotion_rule_id.id, False)


class PromotionDeliveryCase(TransactionCase, AbstractPromotionDeliveryCase):

    def setUp(self, *args, **kwargs):
        super(PromotionDeliveryCase, self).setUp(*args, **kwargs)
        self.set_up()
