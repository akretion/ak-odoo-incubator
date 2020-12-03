# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestSale(common.TransactionCase):
    def setUp(self):
        super(TestSale, self).setUp()
        self.product = self.env.ref("product.product_delivery_02")
        self.product.write({"tracking": "lot", "auto_generate_prodlot": True})
        self.sale = self.env.ref("sale.portal_sale_order_1")
        self.sale_line_config = self.env.ref("sale.portal_sale_order_line_2")

    def test_sale_config_propagaton(self):
        config = {"config_1": 2.5}
        self.sale_line_config.write({"config_text": '{"config_1": 2.5}'})
        self.assertEqual(self.sale_line_config.config, config)
        self.sale.action_confirm()
        self.assertEqual(self.sale_line_config.lot_id.config, config)
