# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.osv import fields, orm

class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_view_delivery(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(
            cr, uid, 'stock', 'action_picking_tree')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of delivery orders to display
        pick_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            pick_ids += [picking.id for picking in so.picking_ids]

	# Custom TODO FIX in 10
	pick_ids += self.pool['stock.picking.out'].search(cr, uid, [
            ('repair_sale_id', 'in', ids),
            ], context=context)
	# Custom end

        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',["+','.join(map(str, pick_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result
