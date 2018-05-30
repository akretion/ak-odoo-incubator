# -*- coding: utf-8 -*-
# © 2018 Akretion Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

import logging

_logger = logging.getLogger(__name__)

# Todo !
# Y'a des bugs ValueError: Expected singleton: product.category(6, 4, 5)
# or
# child = All / Selleable
# child.child_id = product.category(6,4,5)
# bug qui se produit dans le get_domain :  ['child_id', 'parent_of', child.id]
# depuis l'UI ça passe, donc étrange. Bref, à voir peut être un jour -- Raph


@common.post_install(True)
class TestPosAvailableCategory(common.TransactionCase):
    def get_ctx(self, obj):
        return obj.with_context(
            force_company=self.user_company_1.company_id.id).sudo(
            self.user_company_1.id)

    def setUp(self):
        super(TestPosAvailableCategory, self).setUp()
        self.category_1_id = self.ref('product.product_category_1')
        company_1 = self.env['res.company'].create(
            {'name': 'Test company 1'})

        self.user_company_1 = self.env['res.users'].create(
            {'name': 'User company 1',
             'login': 'user_company_1',
             'groups_id': [
                 (6, 0, self.env.ref('point_of_sale.group_pos_manager').ids),
                 (6, 0, self.env.ref('stock.group_stock_manager').ids),
             ],
             'company_id': company_1.id,
             'company_ids': [(6, 0, company_1.ids)]})

        self.my_env = self.get_ctx(self.env['product.category'])

        c_all = self.my_env.search([])
        c_all.write({'available_in_pos': False})

    def test_ensure_up_propagation(self):
        child = self.my_env.browse(self.category_1_id)
        parent = child.parent_id
        self.assertFalse(child.available_in_pos)
        self.assertFalse(parent.available_in_pos)

        self.get_ctx(child).set_available_in_pos(True)
        self.assertTrue(child.available_in_pos)
        # ensure available propagated to parent
        self.assertTrue(parent.available_in_pos)

        # ensure available not propageted to sibilings
        siblings = parent.child_id
        self.assertEqual(
            len([sibling for sibling in siblings if sibling.available_in_pos]),
            1)

    def test_ensure_no_up_propagation(self):
        """It should not modify the parent when set to False."""
        child = self.my_env.browse(self.category_1_id)
        parent = child.parent_id
        self.get_ctx(child).set_available_in_pos(True)
        self.assertTrue(child.available_in_pos)
        self.assertTrue(parent.available_in_pos)

        self.get_ctx(child).set_available_in_pos(False)
        self.assertFalse(child.available_in_pos)
        self.assertTrue(parent.available_in_pos)

    def test_ensure_down_propagation_1(self):
        """It should modify the child when set to False."""
        child = self.my_env.browse(self.category_1_id)
        parent = child.parent_id
        self.get_ctx(child).set_available_in_pos(True)
        self.assertTrue(child.available_in_pos)
        self.assertTrue(parent.available_in_pos)

        self.get_ctx(parent).set_available_in_pos(False)
        self.assertFalse(parent.available_in_pos)
        self.assertFalse(child.available_in_pos)

