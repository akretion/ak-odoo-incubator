# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TaxCommonCase(TransactionCase):
    def _create_tax(self, amount, inc=False):
        vals = {
            "name": "Tax {} {}".format(amount, inc and "inc" or "exc"),
            "amount_type": "percent",
            "type_tax_user": "sale",
            "amount": amount,
            "price_include": inc,
        }
        if amount == 20:
            vals["tax_group_id"] = self.tax_group.id
        return self.env["account.tax"].create(vals)

    def setUp(self):
        super(TaxCommonCase, self).setUp()
        self.tax_group = self.env["account.tax.group"].create({"name": 20})
        self.tax_inc = self._create_tax(20, inc=True)
        self.tax_exc = self._create_tax(20, inc=False)
        self.tax_exp = self._create_tax(0, inc=False)
        self.fp_tax_exc = self.env["account.fiscal.position"].create(
            {
                "name": "Pro tax exc",
                "tax_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": self.tax_inc.id,
                            "tax_dest_id": self.tax_exc.id,
                        },
                    )
                ],
            }
        )
        self.fp_export = self.env["account.fiscal.position"].create(
            {
                "name": "Export",
                "tax_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": self.tax_inc.id,
                            "tax_dest_id": self.tax_exp.id,
                        },
                    )
                ],
            }
        )
        self.product = self.env.ref("pricelist_tax.product_1")
        self.product.taxes_id = self.tax_inc
