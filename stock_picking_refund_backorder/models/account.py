# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm
from openerp.tools.translate import _


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"

    def _refund_cleanup_lines(self, cr, uid, lines, context=None):
        if context is None:
            context = {}
        res = super(AccountInvoice, self)._refund_cleanup_lines(
            cr, uid, lines, context=context)
        if context.get('cancel_backorder_id') and res:
            id2data = {}
            for key, key2, line in res:
                if not line['product_id'] in id2data:
                    id2data[line['product_id']] = line
                else:
                    equal = ['price_unit', 'discount']
                    for field in equal:
                        if line[field] != id2data[line['product_id']][field]:
                            raise orm.except_orm(
                                _('Error'),
                                _('Same product must have the same price'),
                                )
                    id2data[line['product_id']]['quantity'] += line['quantity']

            result = []
            picking = self.pool['stock.picking'].browse(
                cr, uid, context['cancel_backorder_id'], context=context)
            id2qty = {}
            for move in picking.move_lines:
                id2qty[move.product_id.id] = move.product_qty
            for product_id, qty in id2qty.items():
                line = id2data[product_id]
                line['quantity'] = qty
                result.append((0, 0, line))
            return result
        return res

    def _prepare_refund(self, cr, uid, invoice, date=None, period_id=None,
                        description=None, journal_id=None, context=None):
        res = super(AccountInvoice, self)._prepare_refund(cr, uid, invoice,
            date=date, period_id=period_id, description=description,
            journal_id=journal_id, context=context)
        if context.get('cancel_backorder_id'):
            picking = self.pool['stock.picking'].browse(
                cr, uid, context['cancel_backorder_id'], context=context)
            res.update({
                'sale_ids': [(4, picking.sale_id.id)],
                'origin': picking.name,
                })
        return res
