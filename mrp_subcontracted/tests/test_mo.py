# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestMO(TransactionCase):

    def testMoBlockedUntilPurchased(self):
        """Some basic tests.

        Ensure wait_for_service works
        Ensure states of MO, PO and Procurements are tied.
        """
        bom = self.env.ref('mrp_subcontracted.flour_bom')
        product_flour = self.env.ref('mrp_subcontracted.product_flour')
        vals = {
            'product_id': product_flour.id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'bom_id': bom.id,
        }
        mo = self.env['mrp.production'].create(vals)
        proc = mo.service_procurement_id
        po = proc.purchase_id

        # init state
        self.assertTrue(po.state == 'draft')
        self.assertTrue(proc.state == 'running')
        self.assertTrue(mo.wait_for_service)

        po.button_approve()
        self.assertTrue(po.state == 'purchase')
        self.assertTrue(proc.state == 'done')
        self.assertTrue(not mo.wait_for_service)

        po.button_cancel()
        self.assertTrue(po.state == 'cancel')
        self.assertTrue(proc.state in ('cancel', 'exception'))
        self.assertTrue(mo.wait_for_service)

        po.button_draft()
        self.assertTrue(po.state == 'draft')
        self.assertTrue(proc.state == 'running')
        self.assertTrue(mo.wait_for_service)

    def testPoBlockedIfMoDone(self):
        """If MO is produced PO can't be canceled."""
        bom = self.env.ref('mrp_subcontracted.flour_bom')
        product_flour = self.env.ref('mrp_subcontracted.product_flour')
        vals = {
            'product_id': product_flour.id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'bom_id': bom.id,
        }
        mo = self.env['mrp.production'].create(vals)
        proc = mo.service_procurement_id
        po = proc.purchase_id

        po.button_approve()
        produce_wizard = self.env['mrp.product.produce'].sudo().with_context({
            'active_id': mo.id,
            'active_ids': [mo.id],
        }).create({
            'product_qty': 1.0,
        })
        produce_wizard.do_produce()
        mo.button_mark_done()
        self.assertTrue(po.state == 'purchase')
        self.assertTrue(proc.state == 'done')
        self.assertTrue(mo.state == 'done')
        try:
            po.button_cancel()
            self.assertTrue(False)
        except UserError as err:
            self.assertTrue('Unable to cancel purchase order' in err[0])

        try:
            proc.propagate_cancels()
            self.assertTrue(False)
        except UserError as err:
            self.assertTrue(True)
            # self.assertTrue('Unable to cancel procurement' in err[0])

        self.assertTrue(po.state == 'purchase')
        self.assertTrue(proc.state == 'done')
        self.assertTrue(mo.state == 'done')

    def testMultiplePO(self):
        # in case we use purchase request (and may be blanket order?)
        # we can have multiple order line for one MO
        # So the service procurement can't ping to the right PO
        # The first PO confirmed should take place on srv proc.po_id
        bom = self.env.ref('mrp_subcontracted.flour_bom')
        product_flour = self.env.ref('mrp_subcontracted.product_flour')
        vals = {
            'product_id': product_flour.id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'bom_id': bom.id,
        }
        mo = self.env['mrp.production'].create(vals)
        proc = mo.service_procurement_id
        po = proc.purchase_id
        pol = po.order_line
        po_vals = {
            'partner_id': po.partner_id.id,
        }
        po2 = po.create(po_vals)
        po2.order_line.create({
            'order_id': po2.id,
            'product_id': pol.product_id.id,
            'product_uom': pol.product_uom.id,
            'product_qty': pol.product_qty,
            'price_unit': pol.price_unit,
            'name': pol.name,
            'date_planned': pol.date_planned,
            'mo_id': pol.mo_id.id,
        })

        self.assertTrue(po2.order_line.mo_id == po.order_line.mo_id)
        self.assertTrue(proc.purchase_id == po)
        self.assertFalse(proc.purchase_id == po2)

        po2.button_approve()
        self.assertTrue(po2.order_line.mo_id == po.order_line.mo_id)
        self.assertFalse(proc.purchase_id == po)
        self.assertTrue(proc.purchase_id == po2)
