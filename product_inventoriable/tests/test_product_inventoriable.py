# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestProductProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_product_4 = cls.env.ref("product.product_product_4")

    def _create_inventory_lines(self):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "test inventory",
            }
        )
        inventory.action_start()
        inventory_lines = inventory.line_ids.filtered(
            lambda l: l.product_id == self.product_product_4
        )
        return inventory_lines

    def test_product_to_inventory(self):
        self.product_product_4.write({"to_inventory": True})
        inventory_lines = self._create_inventory_lines()
        self.assertEqual(len(inventory_lines), 1)

    def test_product_not_to_inventory(self):
        self.product_product_4.write({"to_inventory": False})
        inventory_lines = self._create_inventory_lines()
        self.assertEqual(len(inventory_lines), 0)
