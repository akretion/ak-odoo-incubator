# coding: utf-8
#    @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class BaseTest(TransactionCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        self.sale_order_m = self.env['sale.order']
        self.sale_line_m = self.env['sale.order.line']

    def _init_partner_id(self):
        """Search for one partner which can be a customer"""
        self.partner_id = self.env['res.partner'].search(
            [('customer', '=', 'True')])[0].id

    def _init_sale_order(self):
        """ Create a sale order based on list of product ids that are contained
            in self. Uses _init_partner_id.
        """
        # Create sale order_infos_keys
        order_infos = self.sale_order_m.onchange_partner_id(
            self.partner_id)['value']
        vals_sale_order = {
            'partner_id': self.partner_id,
            'pricelist_id': order_infos['pricelist_id'],
            'partner_invoice_id': self.partner_id,
            'partner_shipping_id': self.partner_id,
        }
        self.sale = self.sale_order_m.create(vals_sale_order)
        products = self.env.ref('sale_order_lot_mrp.tracked_product')
        # Sale order lines
        for product in products:
            product.write({'auto_generate_prodlot': True})
            # Get some default values for product quantity
            order_line = self.sale_line_m.product_id_change(
                order_infos['pricelist_id'], product.id,
                qty=1, partner_id=self.partner_id
            )['value']
            order_line['order_id'] = self.sale.id
            order_line['product_id'] = product.id
            self.sale_line_m.create(order_line)
        self.sale.action_button_confirm()


class TestSuccess(BaseTest):
    def setUp(self):
        super(TestSuccess, self).setUp()
        self._init_partner_id()
        self._init_sale_order()

    def _search_procurements(self):
        stock_location = self.env.ref('stock.stock_location_stock')
        return self.env['procurement.order'].search(
            [('group_id.name', '=', self.sale.name),
             ('location_id', '=', stock_location.id)])

    def test_00_mo_create(self):
        """ Check if the create function is setting a move-to-production id
            and a production lot id
        """
        lot_name = self.sale.order_line[0].lot_id.name
        procs = self._search_procurements()
        if procs:
            procs.run()
            production_name = procs[0].production_id.name
        self.assertEquals(
            production_name, lot_name,
            "Incorrect name for Manufacturing Order, should be '%s'" % (
                lot_name))
