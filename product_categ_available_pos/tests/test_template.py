# -*- coding: utf-8 -*-
# © 2018 Akretion Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import common

_logger = logging.getLogger(__name__)


@common.post_install(True)
class TestPosAvailableProduct(common.TransactionCase):
    def get_ctx(self, obj):
        return obj.with_context(
            force_company=self.user_company_1.company_id.id
        ).sudo(self.user_company_1.id)

    def setUp(self):
        super(TestPosAvailableProduct, self).setUp()
        self.category_1_id = self.ref("product.product_category_1")
        company_1 = self.env["res.company"].create({"name": "Test company 1"})

        self.user_company_1 = self.env["res.users"].create(
            {
                "name": "User company 1",
                "login": "user_company_1",
                "groups_id": [
                    (
                        6,
                        0,
                        self.env.ref("point_of_sale.group_pos_manager").ids,
                    ),
                    (6, 0, self.env.ref("stock.group_stock_manager").ids),
                ],
                "company_id": company_1.id,
                "company_ids": [(6, 0, company_1.ids)],
            }
        )

        self.my_env = self.get_ctx(self.env["product.category"])

        c_all = self.my_env.search([])
        c_all.write({"available_in_pos": False})

    def test_ensure_template_propagation(self):
        # si ya un bug expected singleton voir test_category
        cat = self.my_env.browse(self.category_1_id)
        prod = self.get_ctx(self.env["product.template"]).search(
            [["categ_id", "=", cat.id]], limit=1
        )
        self.assertEqual(prod.available_in_pos, cat.available_in_pos)
        self.get_ctx(cat).set_available_in_pos(True)

        self.env.invalidate_all()
        # force clean cache to protect from false negatives

        self.assertEqual(prod.available_in_pos, cat.available_in_pos)
        self.assertTrue(prod.available_in_pos)
