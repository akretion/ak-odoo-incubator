# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.tests.common import TransactionCase

logger = logging.getLogger(__name__)


LINE_MESSAGE = "Line %s has no price %s matching with %s"


class TestPricePolicy(TransactionCase):

    def setUp(self):
        super(TestPricePolicy, self).setUp()
        self._get_prices()

    def _get_prices(self):
        self.prd = self.env.ref('product.product_product_31')
        # pricelists
        self.partner_plist = self.env.ref(
            'sale_team_price_policy.product_pricelist_4_customer')
        self.contract_plist = self.env.ref(
            'sale_team_price_policy.product_pricelist_sale_team')
        # unit prices
        self.partner_price = self.env.ref(
            'sale_team_price_policy.product_pricelist_4_customer')\
            .price_get(self.prd.id, 1)[self.partner_plist.id]
        self.contract_price = self.env.ref(
            'sale_team_price_policy.product_pricelist_sale_team')\
            .price_get(self.prd.id, 1)[self.contract_plist.id]
        # sales
        self.sale_order_partner = self.env.ref(
            'sale_team_price_policy.sale_partner_pricelist')
        self.sale_order_team = self.env.ref(
            'sale_team_price_policy.sale_market_pricelist')

    def test_sale_price(self):
        compare = (
            (self.env.ref(
                'sale_team_price_policy.sale_line_partner_pricelist'),
             self.partner_price),
            (self.env.ref('sale_team_price_policy.sale_line_market_pricelist'),
             self.contract_price),
        )
        for line, pricing in compare:
            self.assertEqual(
                line.price_unit, pricing, LINE_MESSAGE
                % (line, line.price_unit, pricing))

    def test_sale_update_team(self):
        # FIRST SALE
        # intial state
        self.assertEqual(
            self.sale_order_partner.pricelist_id, self.partner_plist)
        res = self.sale_order_partner.onchange_pricelist_id(
            self.env.ref('product.list0').id,
            self.sale_order_partner.order_line)
        # Update pricelist raise a warning
        self.assertNotEquals(res.get('warning', False), False,
                             "Warning waited")
        self.assertEqual(
            self.sale_order_partner.pricelist_id, self.partner_plist,
            "Pricelist not in initial value")
        # SECOND SALE
        self.assertEqual(
            self.sale_order_team.pricelist_id, self.contract_plist)
        res = self.sale_order_team.onchange_pricelist_id(
            self.partner_plist.id,
            self.sale_order_team.order_line)
        # Update pricelist raise a warning
        self.assertNotEquals(res.get('warning', False), False,
                             "Warning waited")
        self.assertEqual(
            self.sale_order_team.pricelist_id, self.contract_plist,
            "Pricelist not in initial value")

    def test_invoice_price(self):
        compare = (
            (self.env.ref(
                'sale_team_price_policy.invoice_line_partner_pricelist'),
             self.partner_price),
            (self.env.ref(
                'sale_team_price_policy.invoice_line_market_pricelist'),
             self.contract_price),
        )
        for line, pricing in compare:
            self.assertEqual(
                line.price_unit, pricing, LINE_MESSAGE
                % (line, line.price_unit, pricing))
