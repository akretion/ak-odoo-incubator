# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TaxCommonCase


class Scenario(object):
    def _get_line(self, fp):
        return self.env["sale.order.line"].new(
            {
                "order_id": {
                    "partner_id": self.env.ref("base.res_partner_10").id,
                    "pricelist_id": self.pricelist.id,
                    "picking_policy": "direct",
                    "fiscal_position_id": fp and fp.id,
                },
                "product_uom_qty": 1,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
            }
        )

    def _test_onchange(self, fp, expected_price_unit, expected_tax):
        line = self._get_line(fp)

        line.product_id_change()
        self.assertEqual(line.price_unit, expected_price_unit)
        self.assertEqual(line.tax_id, expected_tax)

        line.product_uom_change()
        self.assertEqual(line.price_unit, expected_price_unit)
        self.assertEqual(line.tax_id, expected_tax)

    def test_no_fp(self):
        self._test_onchange(
            None,
            expected_price_unit=self.expected_price_tax_inc,
            expected_tax=self.tax_inc,
        )

    def test_tax_exc(self):
        self._test_onchange(
            self.fp_tax_exc,
            expected_price_unit=self.expected_price_tax_exc,
            expected_tax=self.tax_exc,
        )

    def test_fp_export(self):
        self._test_onchange(
            self.fp_export,
            expected_price_unit=self.expected_price_tax_exc,
            expected_tax=self.tax_exp,
        )


class PricelistTaxIncludeCase(Scenario, TaxCommonCase):
    def setUp(self):
        super(PricelistTaxIncludeCase, self).setUp()
        self.pricelist = self.env.ref("pricelist_tax.pricelist_tax_inc")
        self.expected_price_tax_inc = 24
        self.expected_price_tax_exc = 20


class PricelistTaxExcludeCase(Scenario, TaxCommonCase):
    def setUp(self):
        super(PricelistTaxExcludeCase, self).setUp()
        self.pricelist = self.env.ref("pricelist_tax.pricelist_tax_exc")
        self.expected_price_tax_inc = 12
        self.expected_price_tax_exc = 10
