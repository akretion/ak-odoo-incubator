# © 2019 Akretion David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestReplaceComponent(TransactionCase):

    def setUp(self):
        super(TestReplaceComponent, self).setUp()

    def test_replace(self):
        mo = self.env.ref('mrp.mrp_production_1')
        mo.button_unreserve()
        product_ids = [
            self.env.ref('product.product_product_16').id,
            self.env.ref('product.product_product_13').id]
        wiz = self.env['replace.component.transient'].create(
            {'production_id': mo.id,
             'product_ids': [(0, 0, product_ids)],
             # office chair
             'product_id': self.env.ref('product.product_product_12').id,
             })
        wiz.apply_replacement()
        mo.action_assign()
        produce = self.env['mrp.product.produce'].with_context(
            active_id=mo.id).create({'product_qty': mo.product_qty})
        produce.do_produce()
        mo.button_mark_done()
        self.assertEqual(mo.move_raw_ids[0].product_uom_qty,
                         mo.move_raw_ids[0].quantity_done)
        self.assertEqual(mo.move_raw_ids[1].product_uom_qty,
                         mo.move_raw_ids[1].quantity_done)
