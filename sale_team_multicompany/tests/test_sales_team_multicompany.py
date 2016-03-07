# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.osv.osv import except_orm as AccessError


class TestSalesTeamMultiCompany(TransactionCase):
    def test_company_1(self):
        self.assertEqual(self.crm_case_section1.company_id, self.res_company1)
        # All of this should be allowed
        self.crm_case_section1.sudo(self.res_users1).name = "Test 1"
        self.crm_case_section_both.sudo(self.res_users1).name = "Test 2"
        # And this one not
        with self.assertRaises(AccessError):
            self.crm_case_section2.sudo(self.res_users1).name = "Test"

    def test_company_2(self):
        self.assertEqual(self.crm_case_section2.company_id, self.res_company2)
        # All of this should be allowed
        self.crm_case_section2.sudo(self.res_users2).name = "Test 1"
        self.crm_case_section_both.sudo(self.res_users2).name = "Test 2"
        # And this one not
        with self.assertRaises(AccessError):
            self.crm_case_section1.sudo(self.res_users2).name = "Test"

    def test_create_sale_order(self):
        # All of this should be allowed
        self.env['sale.order'].sudo(self.res_users2).create(
            {'name': 'TEST 1',
             'partner_id': self.res_partner2.id,
             'section_id': self.crm_case_section2.id})
        self.env['sale.order'].sudo(self.res_users1).create(
            {'name': 'TEST 2',
             'partner_id': self.res_partner1.id,
             'section_id': self.crm_case_section_both.id})
        # And this one not
        with self.assertRaises(AccessError):
            self.env['sale.order'].sudo(self.res_users1).create(
                {'name': 'TEST',
                 'partner_id': self.res_partner1.id,
                 'section_id': self.crm_case_section2.id})
