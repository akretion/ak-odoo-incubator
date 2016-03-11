# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as AccessError


class TestSalesTeamMultiCompany(TransactionCase):
    def test_company_1(self):
        res_company1 = self.env.ref('sale_team_multicompany.res_company1')
        crm_case_section1 = self.env.ref(
            'sale_team_multicompany.crm_case_section1')
        crm_case_section2 = self.env.ref(
            'sale_team_multicompany.crm_case_section2')
        crm_case_section_both = self.env.ref(
            'sale_team_multicompany.crm_case_section_both')
        res_users1 = self.env.ref('sale_team_multicompany.res_users1')
        self.assertEqual(crm_case_section1.company_ids[0], res_company1)
        # All of this should be allowed
        crm_case_section1.sudo(res_users1.id).name = "Test 1"
        crm_case_section_both.sudo(res_users1.id).name = "Test 2"
        # And this one not
        with self.assertRaises(AccessError):
            crm_case_section2.sudo(res_users1.id).name = "Test"

    def test_company_2(self):
        res_company2 = self.env.ref('sale_team_multicompany.res_company2')
        crm_case_section1 = self.env.ref(
            'sale_team_multicompany.crm_case_section1')
        crm_case_section2 = self.env.ref(
            'sale_team_multicompany.crm_case_section2')
        crm_case_section_both = self.env.ref(
            'sale_team_multicompany.crm_case_section_both')
        res_users2 = self.env.ref('sale_team_multicompany.res_users2')
        self.assertEqual(crm_case_section2.company_ids[0], res_company2)
        # All of this should be allowed
        crm_case_section2.sudo(res_users2.id).name = "Test 1"
        crm_case_section_both.sudo(res_users2.id).name = "Test 2"
        # And this one not
        with self.assertRaises(AccessError):
            crm_case_section1.sudo(res_users2.id).name = "Test"

    def test_create_sale_order(self):
        res_users1 = self.env.ref('sale_team_multicompany.res_users1')
        res_users2 = self.env.ref('sale_team_multicompany.res_users2')
        res_partner1 = self.env.ref('sale_team_multicompany.res_partner1')
        res_partner2 = self.env.ref('sale_team_multicompany.res_partner2')
        crm_case_section2 = self.env.ref(
            'sale_team_multicompany.crm_case_section2')
        crm_case_section_both = self.env.ref(
            'sale_team_multicompany.crm_case_section_both')
        # All of this should be allowed
        self.env['sale.order'].sudo(res_users2.id).create(
            {'name': 'TEST 1',
             'partner_id': res_partner2.id,
             'section_id': crm_case_section2.id})
        self.env['sale.order'].sudo(res_users1.id).create(
            {'name': 'TEST 2',
             'partner_id': res_partner1.id,
             'section_id': crm_case_section_both.id})
        # And this one not
        with self.assertRaises(AccessError):
            self.env['sale.order'].sudo(res_users1.id).create(
                {'name': 'TEST',
                 'partner_id': res_partner1.id,
                 'section_id': crm_case_section2.id})
