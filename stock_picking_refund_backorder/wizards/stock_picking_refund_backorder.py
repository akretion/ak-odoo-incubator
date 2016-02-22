# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm
import netsvc
from openerp.tools.translate import _


class StockPickingRefundBackorder(orm.TransientModel):
    _name = "stock.picking.refund.backorder"

    def _generate_refund(self, cr, uid, picking_id, invoice_id, context=None):
        #Refund the cancelled picking
        refund_obj = self.pool['account.invoice.refund']
        ctx = context.copy()
        ctx.update({
            'active_ids': [invoice_id],
            'cancel_backorder_id': picking_id,
            })
        refund_vals = refund_obj.default_get(
            cr, uid, ['date', 'journal_id', 'filter_refund', 'description'],
            context=ctx)
        refund_id = refund_obj.create(cr, uid, refund_vals, context=ctx)
        res = refund_obj.invoice_refund(cr, uid, [refund_id], context=ctx)
        for arg in res['domain']:
            if arg[0] == 'id':
                return res, arg[2][0]
	raise orm.except_orm(
	    _('Dev ERROR'),
	    _('invoice method must return the id'))

    def process_cancellation(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        picking = self.pool['stock.picking.out'].browse(
            cr, uid, context['active_id'], context=context)
        wf_service.trg_validate(
            uid, 'stock.picking', picking.id, 'button_cancel', cr)
        wf_service.trg_validate(
            uid, 'sale.order', picking.sale_id.id, 'ship_corrected', cr)
        sale = picking.sale_id.browse()[0]
        if len(sale.invoice_ids) == 0:
            raise orm.except_orm(
                _('Error'),
                _('Failed to generated the invoice'))
        if len(sale.invoice_ids) > 1:
            raise orm.except_orm(
                _('Error'),
                _('Too many invoice found'))

        invoice = sale.invoice_ids[0]

        wf_service.trg_validate(
            uid, 'account.invoice', invoice.id, 'invoice_open', cr)
        action, refund_id = self._generate_refund(
            cr, uid, picking.id, invoice.id, context=context)
        refund = self.pool['account.invoice'].browse(
            cr, uid, refund_id, context=context)
        wf_service.trg_validate(
            uid, 'account.invoice', refund.id, 'invoice_open', cr)
        action.update({
            'domain': [('id', 'in', [refund.id, invoice.id])],
            'name': _('Customer Invoice and Refund'),
            })
        return action
