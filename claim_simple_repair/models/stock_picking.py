# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.osv import fields, orm
from openerp.tools.translate import _


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'repair_sale_id': fields.many2one('sale.order', string='Sale')
        }

    def action_done(self, cr, uid, ids, context=None):
        res = super(StockPicking, self).action_done(
            cr, uid, ids, context=context)
        if self.pool.get('magento.sale.comment'):
            for picking in self.browse(cr, uid, ids, context=context):
                self._notify_magento(cr, uid, picking, context=context)
        return res

    def _notify_magento(self, cr, uid, picking, context=None):
        sale = picking.repair_sale_id
        if sale and sale.magento_bind_ids:
            product = self.pool['product.product'].browse(
                cr, uid, picking.move_lines[0].product.id,
                {'lang': sale.partner_id.lang})
            message = product.rma_out_description
            for magento_bind in sale.magento_bind_ids:
                if '%s' in message:
                    message = message % picking.carrier_tracking_ref
                vals = {
                    'is_visible_on_front': True,
                    'is_customer_notified': True,
                    'magento_sale_order_id': magento_bind.id,
                    'status': 'complete',
                    'body': message,
                    'type': 'notification',
                    }
                self.pool['magento.sale.comment'].create(
                    cr, uid, vals, context=context)


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'repair_sale_id': fields.many2one('sale.order', string='Sale')
        }
