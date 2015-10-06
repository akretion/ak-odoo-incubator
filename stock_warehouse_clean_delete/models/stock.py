# -*- coding: utf-8 -*-
from openerp.osv import orm, fields

class StockWarehouse(orm.Model):
    _inherit = "stock.warehouse"

    def unlink(self, cr, uid, ids, context=None):
        stock_obj = self.pool['stock.location']
        seq_obj = self.pool['ir.sequence']
        type_obj = self.pool['stock.picking.type']
        route_obj = self.pool['stock.location.route']
        for warehouse in self.browse(cr, uid, ids, context=context):
            loc = stock_obj.search(cr, uid, [('name', '=', warehouse.name)])
            if loc:
                children = stock_obj.search(cr, uid, [('location_id', '=', loc[0])])
            else:
                chldren = []
            prefixes = ['IN', 'OUT', 'PACK', 'PICK', 'INT']
            for prefix in prefixes:
                seqs = seq_obj.search(cr, uid, [('prefix', 'ilike', "%s/%s/" % (warehouse.name, prefix))])
            types = type_obj.search(cr, uid, [('warehouse_id', '=', warehouse.id)])
            routes = route_obj.search(cr, uid, [('name', 'ilike', "%s:" % (warehouse.name,))])
        res = super(StockWarehouse, self).unlink(cr, uid, ids, context)
        stock_obj.unlink(cr, uid, loc + children)
        type_obj.unlink(cr, uid, types)
        seq_obj.unlink(cr, uid, seqs)
        route_obj.unlink(cr, uid, routes)
        return res
