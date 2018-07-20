# -*- coding: utf-8 -*-
# Copyright 2016-18 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestGeneratePutaway(TransactionCase):
    """Test that the putaway locations are updated when the method is used"""

    def setUp(self):
        super(TestGeneratePutaway, self).setUp()
        # Get required Model
        self.product_model = self.env['product.product']
        self.template_model = self.env['product.template']
        self.product_ctg_model = self.env['product.category']
        self.account_model = self.env['account.account']
        self.res_users_model = self.env['res.users']
        self.stock_location_model = self.env['stock.location']
        self.stock_inventory_model = self.env['stock.inventory']
        self.stock_inventory_line_model = self.env['stock.inventory.line']

        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')

        # groups
        self.group_stock_user = self.env.ref(
            'stock.group_stock_user')

        location = self.stock_location_model.search([('name', '=', 'WH')])
        self.location = self.stock_location_model.search([('location_id', '=',
                                                           location.id)])

        # Create users
        self.user1 = self._create_user('user_1',
                                       [self.group_stock_user,
                                        self.group_inventory_valuation],
                                       self.company)

        # Create a Product
        self.product_1 = self._create_product(False)
        self.product_2 = self._create_product(self.product_1.product_tmpl_id)

        # Create Inventory
        self.inventory = self._create_inventory('inv1', self.location)
        self._create_inventory_line(self.inventory, self.product_1, 10)
        self._create_inventory_line(self.inventory, self.product_2, 2)

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.res_users_model.with_context(
                {'no_reset_password': True}).create(
                {'name': 'Test User',
                 'login': login,
                 'password': 'demo',
                 'email': 'test@yourcompany.com',
                 'company_id': company.id,
                 'company_ids': [(4, company.id)],
                 'groups_id': [(6, 0, group_ids)]
                 })
        return user

    def _create_product(self, template):
        """Create a Product variant."""
        if not template:
            template = self.template_model.create({
                'name': 'test_product',
                'categ_id': self.product_ctg.id,
                'type': 'product',
                'valuation': 'real_time',
                'property_stock_account_input': self.account_grni.id,
                'property_stock_account_output': self.account_cogs.id,
            })
            return template.product_variant_ids[0]
        product = self.product_model.create({'product_tmpl_id': template.id})
        return product

    def _create_inventory(self, name, location):
        inventory = self.stock_inventory_model.create({
            'name': name,
            'location_id': location.id
        })
        return inventory

    def _create_inventory_line(self, inventory, product, quantity):
        line = self.stock_inventory_line_model.create({
            'inventory_id': inventory.id,
            'product_id': product.id,
            'product_qty': quantity,
        })
        return line

    def test_generate(self):
        """Test default methods"""
        self.inventory.generate_putaway_strategy()
        self.assertEquals(
            len(self.product_1.product_putaway_ids), 2,
            'pas le bon nombre de putaway strategy créées')
