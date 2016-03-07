# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.osv.osv import except_orm as AccessError


class TestSalesTeamMultiCompany(TransactionCase):
    def test_company_1(self):
        self.assertEqual(self.sales_team_company_1.company_id, self.company_1)
        # All of this should be allowed
        self.sales_team_company_1.sudo(self.user_company_1).name = "Test"
        self.sales_team_company_both.sudo(self.user_company_1).name = "Test"
        # And this one not
        with self.assertRaises(AccessError):
            self.sales_team_company_2.sudo(self.user_company_1).name = "Test"

    def test_company_2(self):
        self.assertEqual(self.sales_team_company_2.company_id, self.company_2)
        # All of this should be allowed
        self.sales_team_company_2.sudo(self.user_company_2).name = "Test"
        self.sales_team_company_both.sudo(self.user_company_2).name = "Test"
        # And this one not
        with self.assertRaises(AccessError):
            self.sales_team_company_1.sudo(self.user_company_2).name = "Test"

    def test_create_sale_order(self):
        # All of this should be allowed
        self.env['sale.order'].sudo(self.user_company_2).create(
            {'name': 'TEST',
             'partner_id': self.partner_2.id,
             'section_id': self.sales_team_company_2.id})
        self.env['sale.order'].sudo(self.user_company_1).create(
            {'name': 'TEST',
             'partner_id': self.partner_1.id,
             'section_id': self.sales_team_company_both.id})
        # And this one not
        with self.assertRaises(AccessError):
            self.env['sale.order'].sudo(self.user_company_1).create(
                {'name': 'TEST',
                 'partner_id': self.partner_1.id,
                 'section_id': self.sales_team_company_2.id})
