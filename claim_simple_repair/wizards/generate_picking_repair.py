# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.osv import fields, orm
from openerp import netsvc


class GeneratePickingRepair(orm.Model):
    _name = 'generate.picking.repair'
    _description = 'Generate Picking Repair'

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            string='Produit',
            required=True,
            readonly=True),
        'description': fields.char(
            string='Description',
            required=True),
        }

    def _get_default_product(self, cr, uid, context=None):
        __, product_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'claim_simple_repair', 'product_product_repair')
        return product_id

    _defaults = {
        'product_id': _get_default_product,
        }

    def _prepare_move_line(self, cr, uid, ids, order, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': wizard.description,
            'product_id': wizard.product_id.id,
            'product_qty': 1,
            'product_uom': wizard.product_id.uom_id.id,
            'partner_id': order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'tracking_id': False,
            'state': 'draft',
            'company_id': order.company_id.id,
        }

    def _notify_magento(self, cr, uid, sale, context=None):
        if sale.magento_bind_ids:
            for magento_bind in sale.magento_bind_ids:
                vals = {
                    'is_visible_on_front': True,
                    'is_customer_notified': True,
                    'magento_sale_order_id': magento_bind.id,
                    'status': 'started',
                    'body': u'Votre commande est en cours de réparation',
                    'type': 'notification',
                    }
                self.pool['magento.sale.comment'].create(
                    cr, uid, vals, context=context)

    def validate(self, cr, uid, ids, context=None):
        sale_obj = self.pool['sale.order']
        picking_obj = self.pool['stock.picking.out']
        sale = sale_obj.browse(cr, uid, context['active_id'], context=context)
        vals = sale_obj._prepare_order_picking(cr, uid, sale, context=context)
        vals['repair_sale_id'] = sale.id
        vals['sale_id'] = None
        vals['origin'] = u'SAV ' + vals['origin']
        line_vals = self._prepare_move_line(
            cr, uid, ids, sale, context=context)
        vals['move_lines'] = [(0, 0, line_vals)]
        picking_id = picking_obj.create(
            cr, uid, vals, context=context)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            uid, 'stock.picking', picking_id, 'button_confirm', cr)
        picking_obj.force_assign(cr, uid, [picking_id], context)
        # notify magento if installed
        if self.pool.get('magento.sale.comment'):
            self._notify_magento(cr, uid, sale, context=context)
        __, action_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'stock', 'action_picking_tree')
        action = self.pool['ir.actions.act_window'].read(
            cr, uid, action_id, context=context)
        action['domain'] = [('id', '=', picking_id)]
        return action
