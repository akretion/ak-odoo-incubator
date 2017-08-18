# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.tests.common import TransactionCase

logger = logging.getLogger(__name__)


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
                line.price_unit, pricing,
                "Sale line %s has no price %s matching with %s"
                % (line, line.price_unit, pricing))
