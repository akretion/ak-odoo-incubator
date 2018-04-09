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
        mo = self.env.ref('mrp_subcontracted.mrp_flour_mo')
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
        self.assertTrue(proc.state == 'exception')
        self.assertTrue(mo.wait_for_service)

        po.button_draft()
        self.assertTrue(po.state == 'draft')
        self.assertTrue(proc.state == 'running')
        self.assertTrue(mo.wait_for_service)

    def testPoBlockedIfMoDone(self):
        """If MO is produced PO can't be canceled."""
        mo = self.env.ref('mrp_subcontracted.mrp_flour_mo')
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
        self.assertTrue(po.state == 'purchase')
        self.assertTrue(proc.state == 'done')
        self.assertTrue(mo.state == 'done')

