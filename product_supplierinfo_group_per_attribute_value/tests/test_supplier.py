# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.product_supplierinfo_per_attribute_value.tests.test_supplier import (
    TestSupplier,
)


class TestSupplierGroup(TestSupplier):
    def test_add_new_supplier_with_attribute(self):
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [(6, 0, [self.pav_alu.id])],
                "name": self.partner.id,
                "price": 10,
                "min_qty": 10,
            }
        )
        # we should have 2 lines now
        self.assertEqual(len(supplierinfo.group_id.supplierinfo_ids), 2)

    def test_add_supplier_with_several_attribute(self):
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [
                    (6, 0, [self.pav_alu.id, self.pav_steel.id])
                ],
                "name": self.partner.id,
                "price": 10,
                "min_qty": 0,
            }
        )
        # should created a new group
        self.assertEqual(len(supplierinfo.group_id.supplierinfo_ids), 1)

        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [
                    (6, 0, [self.pav_alu.id, self.pav_steel.id])
                ],
                "name": self.partner.id,
                "price": 5,
                "min_qty": 10,
            }
        )
        # should have added a supplierinfo to the group
        self.assertEqual(len(supplierinfo.group_id.supplierinfo_ids), 2)

        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": self.template.id,
                "product_attribute_value_ids": [(6, 0, [self.pav_alu.id])],
                "name": self.partner.id,
                "price": 10,
                "min_qty": 10,
            }
        )
        # should have added a supplierinfo to the demo existing group
        self.assertEqual(len(supplierinfo.group_id.supplierinfo_ids), 2)
