# coding: utf-8
#    @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class BaseTest(TransactionCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        self.product_m = self.env['product.product']
        self.sale_order_m = self.env['sale.order']
        self.sale_line_m = self.env['sale.order.line']

    def _init_products(self):
        """ Initialize lists of products available for the tests
        """
        self.products = []
        # Product 1 : Tracked product
        mto = self.env.ref('stock.route_warehouse0_mto').id
        manuf = self.env.ref('mrp.route_warehouse0_manufacture').id
        vals_1 = {
            'name': 'Tracked product',
            'type': 'product',
            'sale_ok': True,
            'route_ids': [(6, 0, [mto, manuf])],
            'auto_generate_prodlot': True,
        }
        self.products.append(
            self.product_m.create(vals_1)
        )

    def _init_partner_id(self):
        """Search for one partner which can be a customer"""
        self.partner_id = self.env['res.partner'].search(
            [('customer', '=', 'True')])[0].id

    def _init_sale_order(self):
        """ Create a sale order based on list of product ids that are contained
            in self. Uses _init_product_ids and _init_partner_id.
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
        # Sale order lines
        for product in self.products:
            # Get some default values for product quantity
            # produ = self.sale_line_m.onchange_product_id(product.id)['value']
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
        self._init_products()
        self._init_partner_id()
        self._init_sale_order()

    def test_00_mo_create(self):
        """ Check if the create function is setting a move-to-production id
            and a production lot id
        """
        lot_name = self.sale.order_line[0].lot_id.name
        stock_location = self.env.ref('stock.stock_location_stock')
        procs = self.env['procurement.order'].search(
            [('group_id.name', '=', self.sale.name),
             ('location_id', '=', stock_location.id)])
        if procs:
            procs.run(autocommit=True)
            procs.check()
            production_name = procs[0].production_id.name
            print production_name, 'production_name', lot_name

        # self.assertEquals(
        #     production_name, lot_name,
        #     "Incorrect name for Manufacturing Order"
        # )

        # move_prod = order_line.move_ids[0]
        # onchange = self.mrp_prod_obj.product_id_change(
        #     cr, uid, [], order_line.product_id.id
        # )['value']
        # mo_vals = {
        #     'product_id': order_line.product_id.id,
        #     'bom_id': onchange['bom_id'],
        #     'product_qty': 1.0,
        #     'origin': sale_order.name,
        #     'move_prod_id': move_prod.id,
        #     'product_uom': onchange['product_uom'],
        #     'routing_id': onchange['routing_id'],
        # }
        # mo_id = self.mrp_prod_obj.create(
        #     cr, uid, mo_vals
        # )
        # mo = self.mrp_prod_obj.browse(cr, uid, mo_id)

        # if move_prod.lot_id:
        #     self.assertEquals(
        #         mo.move_prod_id.id, mo_vals['move_prod_id'],
        #         "Incorrect move to production id"
        #     )
