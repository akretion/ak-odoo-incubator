# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

# TODO: add tests with purchase requests
# remove dead code


class TestChangeSupplier(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestChangeSupplier, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.oven_wh = self.env.ref('mrp_subcontract_location.OvenWH')
        self.mill_wh = self.env.ref('mrp_subcontract_location.MillWH')
        self.mill_alt_wh = self.env.ref('mrp_subcontract_location.Mill2WH')
        self.oven_alt_wh = self.env.ref('mrp_subcontract_location.Oven2WH')
        self.main_wh = self.env.ref('stock.warehouse0')
        self.oven_loc = self.oven_wh.lot_stock_id
        self.oven_alt_loc = self.oven_alt_wh.lot_stock_id
        self.mill_loc = self.mill_wh.lot_stock_id
        self.mill_alt_loc = self.mill_alt_wh.lot_stock_id

        self.oven_picking_type_id = self.oven_wh.manu_type_id
        self.mill_picking_type_id = self.mill_wh.manu_type_id
        self.main_picking_type_id = self.main_wh.manu_type_id
        self.mill_alt_picking_type_id = self.mill_alt_wh.manu_type_id
        self.oven_alt_picking_type_id = self.oven_alt_wh.manu_type_id

        self.manufacture_route = self.env.ref(
            'mrp.route_warehouse0_manufacture')
        self.buy_route = self.env.ref('purchase.route_warehouse0_buy')
        self.mto_route = self.env.ref('stock.route_warehouse0_mto')
        self.uom_unit = self.env.ref('product.product_uom_unit')

        self.wiz =\
            self.env['purchase.request.line.make.purchase.order']

        self.sandwich = self.env.ref(
            'mrp_subcontract_location.product_sandwich')
        self.bread = self.env.ref(
            'mrp_subcontract_location.product_bread')
        self.sliced_bread = self.env.ref(
            'mrp_subcontract_location.product_sliced_bread')
        self.yeast = self.env.ref(
            'mrp_subcontract_location.product_yeast')
        self.flour = self.env.ref(
            'mrp_subcontracted.product_flour')
        self.grain = self.env.ref(
            'mrp_subcontracted.product_grain')
        self.bread_bom = self.env.ref(
            'mrp_subcontract_location.bread_bom')
        self.sliced_bom = self.env.ref(
            'mrp_subcontract_location.sliced_bread_bom')
        self.sandwich_bom = self.env.ref(
            'mrp_subcontract_location.sandwich_bom')
        self.flour_bom = self.env.ref(
            'mrp_subcontracted.flour_bom')
        self.service_baking = self.env.ref(
            'mrp_subcontract_location.service_baking')
        self.service_milling = self.env.ref(
            'mrp_subcontracted.service_milling')
        self.service_slice = self.env.ref(
            'mrp_subcontract_location.service_slice')
        self.partner_mill = self.env.ref(
            'mrp_subcontracted.partner_mill')
        self.partner_oven = self.env.ref(
            'mrp_subcontract_location.partner_oven')
        self.partner_oven_alt = self.env.ref(
            'mrp_subcontract_location.partner_oven_alternative')
        self.partner_mill_alt = self.env.ref(
            'mrp_subcontract_location.partner_mill_alternative')
        self.bread_bom.picking_type_id = self.oven_picking_type_id
        self.sliced_bom.picking_type_id = self.oven_picking_type_id
        self.flour_bom.picking_type_id = self.mill_picking_type_id
        self.sandwich_bom.picking_type_id = self.main_picking_type_id
        # TODO: don't know why it doesnt work by xml
        flour_alt_route = self.env['mrp.bom']._get_supply_route(
            self.oven_alt_wh, self.mill_wh)

        self.flour.mrp_mts_mto_location_ids = [
            (6, 0, [self.stock_location_stock.id])]
        self.grain.mrp_mts_mto_location_ids = [
            (6, 0, [self.stock_location_stock.id])]
        self.flour.route_ids = [
            (6, 0, [self.buy_route.id, flour_alt_route.id])]
        self.grain.route_ids = [
            (6, 0, [self.buy_route.id, self.mto_route.id])]
        self.grain.purchase_request = True
        # we have to do it twice, don't know why
        self.env['mrp.bom'].search([]).compute_product_routes_cron()
        self.env['mrp.bom'].search([]).compute_product_routes_cron()

    def _get_production_vals(self, prod, qty):
        if prod == self.bread:
            bom = self.bread_bom
        elif prod == self.flour:
            bom = self.flour_bom
        elif prod == self.sandwich:
            bom = self.sandwich_bom
        elif prod == self.sliced_bread:
            bom = self.sliced_bom
        return {
            'product_id': prod.id,
            'product_qty': qty,
            'product_uom_id': self.uom_unit.id,
            'bom_id': bom.id,
        }

    def _update_product_qty(self, product, location, quantity):
        """Update Product quantity."""
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def approve_purchase_request(self, procurement):
        purchase_request = procurement.request_id
        self.assertEquals(len(purchase_request), 1)

        purchase_request.button_to_approve()
        purchase_request.button_approved()
        return purchase_request.line_ids

    def create_rfq_from_prl(self, purchase_request_line):
        vals = {
            'supplier_id': self.partner_adhesive.id,
        }
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id,).create(vals)
        wiz_id.make_purchase_order()

    def prepare_data(self):
        """Prepare a MO of bread.
        It should create:
            - mo of bread at oven wh
            - a buy of oven location (service)
            - a picking in of flour in oven wh
            - a picking out of flour in mill wh
            - mo of flour at mill wh
            - a buy of mill location (service)
            - a buy of grain at mill wh
            """
        # create a procurement
        self.prod_sandwich = self.production_model.create(
            self._get_production_vals(self.sandwich, qty=5))
        self.prod_sandwich.action_assign()

        group_proc = self.prod_sandwich.procurement_group_id
        proc_sand = group_proc.procurement_ids.filtered(
            lambda x: x.product_id == self.bread
        ).filtered('production_id')

        self.prod_bread = proc_sand.production_id

        # ensure service creation
        pol = self.env['purchase.order.line'].search(
            [['mo_id', '=', self.prod_bread.id]])

        self.assertEquals(pol.product_id.id, self.service_baking.id)
        self.assertEquals(
            pol.product_qty, self.prod_bread.product_qty,
            'It should be the same qty in po service as of')

        self.assertEquals(
            self.prod_bread.picking_type_id,
            self.oven_picking_type_id,
            'picking type of oven should be well placed by default')

        self.prod_bread.action_assign()
        flour_move = self.prod_bread.move_raw_ids.filtered(
            lambda x: x.product_id == self.flour)
        self.assertEquals(
            flour_move.location_id,
            self.oven_loc,
            'raw mat should be taken from the oven stock')

        # ensure picking in
        incoming_flour = flour_move.move_orig_ids

        self.assertEquals(
            incoming_flour.picking_id.picking_type_id,
            self.oven_wh.in_type_id,
            'raw mat should come from a picking in'
            # because there is no stock
        )
        self.assertEquals(
            incoming_flour.picking_id.partner_id,
            self.partner_mill,
            'raw mat should come from mill partner'
            # because there is no stock
        )

        # ensure picking out
        outcoming_flour = incoming_flour.move_orig_ids
        self.assertEquals(
            outcoming_flour.picking_id.picking_type_id,
            self.mill_wh.out_type_id,
            'finished mat should be sent by a picking out'
        )
        self.assertEquals(
            outcoming_flour.picking_id.partner_id,
            self.partner_oven,
            'finished mat should be sent to oven partner'
            # because there is no stock
        )

        self.flour_prod = outcoming_flour.move_orig_ids.production_id
        flour_pol = self.env['purchase.order.line'].search(
            [['mo_id', '=', self.flour_prod.id]])

        flour_purchase = flour_pol.order_id
        self.assertEquals(flour_purchase.partner_id, self.partner_mill)

    def testChangeSupplier0Stock(self):
        """Some basic tests.
        Do tests with 0 stock.
        Unneeded materials should be canceled
        Ensure new buy (yeast)
        Ensure new PO (flour)
        """
        self._update_product_qty(
            self.bread, self.oven_loc, 0)
        self._update_product_qty(
            self.flour, self.oven_loc, 0)
        self._update_product_qty(
            self.yeast, self.oven_loc, 0)
        self._update_product_qty(
            self.flour, self.oven_alt_loc, 0)
        self._update_product_qty(
            self.yeast, self.oven_alt_loc, 0)
        self._update_product_qty(
            self.grain, self.mill_loc, 0)

        self.prepare_data()

        pol = self.env['purchase.order.line'].search(
            [['mo_id', '=', self.prod_bread.id]])
        bread_purchase = pol.order_id
        self.assertEquals(
            bread_purchase.partner_id, self.partner_oven,
            'Default supplier for bread')

        group_proc = self.prod_sandwich.procurement_group_id
        proc_flour = group_proc.procurement_ids.filtered(
            lambda x: x.product_id == self.flour
        ).filtered('production_id')

        # we back up some records to test against it later
        first_prod_flour = proc_flour.production_id
        first_pol_flour = self.env['purchase.order.line'].search(
            [['mo_id', '=', first_prod_flour.id]])

        # here we choose another supplier
        bread_purchase.partner_id = self.partner_oven_alt
        # make it effective (buy the service)
        bread_purchase.button_approve()

        self.assertEquals(
            self.prod_bread.picking_type_id,
            self.oven_alt_picking_type_id,
            'picking type id of the MO should change'
        )

        # look at the output
        bread_next_move = self.prod_bread.move_finished_ids.move_dest_id
        self.assertEquals(
            bread_next_move.picking_id.partner_id,
            self.main_wh.partner_id,
            'picking out address should stay the same'
        )

        self.assertEquals(
            bread_next_move.picking_type_id.default_location_src_id,
            self.oven_alt_loc,
            'it should go out from the right stock',
        )

        # look at the input
        # because in this case we don't have any stock
        # and we didn't confirm any po
        # old PO flour should be cancelled
        # old PO yeast should be cancelled
        # a new PO should be created
        yeast_move = self.prod_bread.move_raw_ids.filtered(
            lambda x: x.product_id == self.yeast and x.state != 'cancel')
        yeast_proc = self.env['procurement.order'].search(
            [['move_dest_id', '=', yeast_move.id]])
        self.assertEquals(
            yeast_proc.state, 'running',
            'Buy product procurement should be running')
        self.assertEquals(
            yeast_proc.purchase_id.picking_type_id,
            self.oven_alt_wh.in_type_id,
            'Buy should be at the good place')

        flour_move = self.prod_bread.move_raw_ids.filtered(
            lambda x: x.product_id == self.flour and x.state != 'cancel')

        # ensure picking in
        incoming_flour = flour_move.move_orig_ids
        self.assertEquals(
            incoming_flour.picking_id.picking_type_id,
            self.oven_alt_wh.in_type_id,
            'raw mat should come from a picking in'
            # because there is no stock
        )
        self.assertEquals(
            incoming_flour.picking_id.partner_id,
            self.partner_mill,
            'raw mat should come from mill partner'
            # because there is no stock
        )

        # check old stuff
        self.assertFalse(first_pol_flour.exists())
        self.assertTrue(first_prod_flour.state == 'cancel')

        proc_flour = group_proc.procurement_ids.filtered(
            lambda x: x.product_id == self.flour and x.state == 'running'
        ).filtered('production_id')

        # check new stuff
        new_prod_flour = proc_flour.production_id
        self.assertTrue(new_prod_flour.state == 'confirmed')
        new_pol_flour = self.env['purchase.order.line'].search(
            [['mo_id', '=', new_prod_flour.id]])
        self.assertTrue(new_pol_flour.state == 'draft')
        return

    def testChangeSupplierSomeStock(self):
        """Some basic tests.
        Do tests with 0 stock.
        Unneeded materials should be canceled
        Ensure new buy (yeast)
        Ensure new PO (flour)
        """
        self._update_product_qty(
            self.flour, self.oven_loc, 0)
        self._update_product_qty(
            self.yeast, self.oven_loc, 0)
        self._update_product_qty(
            self.flour, self.oven_alt_loc, 100)
        self._update_product_qty(
            self.yeast, self.oven_alt_loc, 100)

        self.prepare_data()

        pol = self.env['purchase.order.line'].search(
            [['mo_id', '=', self.prod_bread.id]])
        bread_purchase = pol.order_id
        self.assertEquals(
            bread_purchase.partner_id, self.partner_oven,
            'Default supplier for bread')

        group_proc = self.prod_sandwich.procurement_group_id
        proc_flour = group_proc.procurement_ids.filtered(
            lambda x: x.product_id == self.flour
        ).filtered('production_id')

        # we back up some records to test against it later
        first_prod_flour = proc_flour.production_id
        first_pol_flour = self.env['purchase.order.line'].search(
            [['mo_id', '=', first_prod_flour.id]])

        # here we choose another supplier
        bread_purchase.partner_id = self.partner_oven_alt
        # make it effective (buy the service)
        bread_purchase.button_approve()

        self.assertEquals(
            self.prod_bread.picking_type_id,
            self.oven_alt_picking_type_id,
            'picking type id of the MO should change'
        )

        # look at the output
        bread_next_move = self.prod_bread.move_finished_ids.move_dest_id
        self.assertEquals(
            bread_next_move.picking_id.partner_id,
            self.main_wh.partner_id,
            'picking out address should stay the same'
        )

        self.assertEquals(
            bread_next_move.picking_type_id.default_location_src_id,
            self.oven_alt_loc,
            'it should go out from the right stock',
        )

        # look at the input
        # because in this case we do have lot of stock
        # old PO flour should be cancelled
        # old PO yeast should be cancelled
        # no new PO should be created
        yeast_move = self.prod_bread.move_raw_ids.filtered(
            lambda x: x.product_id == self.yeast and x.state != 'cancel')
        yeast_proc = self.env['procurement.order'].search(
            [['move_dest_id', '=', yeast_move.id]])
        self.assertFalse(
            yeast_proc.exists(),
            'There should be not buy of yeast')

        flour_move = self.prod_bread.move_raw_ids.filtered(
            lambda x: x.product_id == self.flour and x.state != 'cancel')

        # ensure not picking in
        incoming_flour = flour_move.move_orig_ids
        self.assertFalse(
            incoming_flour.exists(),
            'raw mat should come from stock'
            # because there is stock
        )

        # check old stuff
        self.assertFalse(first_pol_flour.exists())
        self.assertTrue(first_prod_flour.state == 'cancel')

        proc_flour = group_proc.procurement_ids.filtered(
            lambda x: x.product_id == self.flour and x.state == 'running'
        ).filtered('production_id')

        return

    def testNoOutgoingMove(self):
        """Ensure we can have a PO for
        creating a stock (no outgoing move)
        """
        self._update_product_qty(
            self.bread, self.oven_loc, 0)
        self._update_product_qty(
            self.sliced_bread, self.oven_loc, 0)

        self.sliced_prod = self.production_model.create(
            self._get_production_vals(self.sliced_bread, qty=1))

        po = self.sliced_prod.service_procurement_id.purchase_id
        po.button_confirm()

        # don't know why sliced prod is misplaced here
        # so we action asign after changing location (po confirmed)
        self.sliced_prod.action_assign()

        bread_prod = self.sliced_prod.move_raw_ids.filtered(
            lambda s: s.state != 'cancel').move_orig_ids.production_id

        self.assertEquals(bread_prod.product_id, self.bread)

        pol = self.env['purchase.order.line'].search(
            [['mo_id', '=', bread_prod.id]])
        self.assertEquals(len(pol), 1, 'Too many records for the test')
        self.assertEquals(
            len(pol.order_id.order_line), 1, 'Too many records for the test')
        pol.order_id.button_confirm()
        # never reached if picking_type_id is empty in move.assign_picking()
        # for production moves
        self.assertTrue(True)
