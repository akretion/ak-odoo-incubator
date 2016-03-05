# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import TransactionCase


class DeleteWarehouse(TransactionCase):

    def test_warehouse_clean_delete(self):
        model_to_check = [
            'stock.location',
            'stock.picking.type',
            'stock.location.route',
            'procurement.rule',
            'ir.sequence',
            ]

        record_number = {}
        for model in model_to_check:
            record_number[model] = self.env[model].search_count([])

        warehouse = self.env['stock.warehouse'].create({
            'name': 'Test warehouse',
            'code': 'TW',
            })
        warehouse.unlink()
        for model in model_to_check:
            expected = record_number[model]
            found = self.env[model].search_count([])
            self.assertEqual(
                expected, found,
                msg="Model %s should have %s records instead of %s"
                    % (model, expected, found))

    def test_warehouse_clean_delete_with_empty_vals(self):
        model_to_check = [
            'stock.location',
            'stock.picking.type',
            'stock.location.route',
            'procurement.rule',
            'ir.sequence',
            ]

        record_number = {}
        for model in model_to_check:
            record_number[model] = self.env[model].search_count([])

        warehouse = self.env['stock.warehouse'].create({
            'name': 'Test warehouse',
            'code': 'TW',
            })
        warehouse.pick_type_id.unlink()
        warehouse.unlink()
        for model in model_to_check:
            expected = record_number[model]
            found = self.env[model].search_count([])
            self.assertEqual(
                expected, found,
                msg="Model %s should have %s records instead of %s"
                    % (model, expected, found))
