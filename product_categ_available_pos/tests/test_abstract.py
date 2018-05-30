# -*- coding: utf-8 -*-
# © 2018 Akretion Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


@common.post_install(True)
class TestPosAbstract(common.TransactionCase):
    def get_ctx(self, obj):
        return obj.with_context(
            force_company=self.user_company_1.company_id.id).sudo(
            self.user_company_1.id)

    def setUp(self):
        super(TestPosAbstract, self).setUp()
        self.category_1_id = self.ref('product.product_category_1')
        group_user = self.env.ref('sales_team.group_sale_manager')
        company_1 = self.env['res.company'].create(
            {'name': 'Test company 1'})

        self.user_company_1 = self.env['res.users'].create(
            {'name': 'User company 1',
             'login': 'user_company_1',
             'groups_id': [
                 (6, 0, group_user.ids)],
             'company_id': company_1.id,
             'company_ids': [(6, 0, company_1.ids)]})

        self.my_env = self.get_ctx(self.env['product.category'])

        c_all = self.my_env.search([])
        c_all.write({'available_in_pos': False})

    def test_search_read(self):
        prod = self.get_ctx(self.env['product.template']).search(
            [['categ_id', '=', self.category_1_id]], limit=1)
        cat = self.my_env.browse(self.category_1_id)
        self.get_ctx(cat).set_available_in_pos(True)
        # search read
        p2 = self.get_ctx(prod).search_read([
            ['id', '=', prod.id],
            ['available_in_pos', '=', True]
        ], fields=['id'])
        self.assertEqual(prod.id, p2.id)

    def test_search(self):
        prod = self.get_ctx(self.env['product.template']).search(
            [['categ_id', '=', self.category_1_id]], limit=1)
        cat = self.my_env.browse(self.category_1_id)
        self.get_ctx(cat).set_available_in_pos(True)
        # search
        p3 = self.get_ctx(prod).search([
            ['id', '=', prod.id],
            ['available_in_pos', '=', True]
        ])
        self.assertEqual(prod.id, p3.id)
