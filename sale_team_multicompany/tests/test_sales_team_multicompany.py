# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.osv.osv import except_orm as AccessError


class TestSalesTeamMultiCompany(TransactionCase):
    def setUp(self):
        super(TestSalesTeamMultiCompany, self).setUp()
        self.company_1 = self.env['res.company'].create(
            {'name': 'Test company 1'})
        self.company_2 = self.env['res.company'].create(
            {'name': 'Test company 2'})
        self.sales_team_company_1 = self.env['crm.case.section'].create(
            {'name': 'Sales Team from company 1',
             'company_ids': [(6, 0, self.company_1.ids)]})
        self.sales_team_company_2 = self.env['crm.case.section'].create(
            {'name': 'Sales Team from company 2',
             'company_ids': [(6, 0, self.company_2.ids)]})
        self.sales_team_company_both = self.env['crm.case.section'].create(
            {'name': 'Sales Team for both companies',
             'company_ids': [(6, 0, (self.company_1 + self.company_2).ids)]})
        self.user_company_1 = self.env['res.users'].create(
            {'name': 'User company 1',
             'login': 'user_company_1',
             'groups_id': [
                 (6, 0, self.env.ref('base.group_sale_manager').ids)],
             'company_id': self.company_1.id,
             'company_ids': [(6, 0, self.company_1.ids)]})
        self.user_company_2 = self.env['res.users'].create(
            {'name': 'User company 2',
             'login': 'user_company_2',
             'groups_id': [
                 (6, 0, self.env.ref('base.group_sale_manager').ids)],
             'company_id': self.company_2.id,
             'company_ids': [(6, 0, self.company_2.ids)]})
        self.partner_1 = self.env['res.partner'].create(
            {'name': 'Test partner 1'})

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
        with self.assertRaises(AccessError):
            self.env['sale.order'].sudo(self.user_company_1).create(
                {'name': 'TEST',
                 'partner_id': self.partner_1.id,
                 'section_id': self.sales_team_company_2.id})
