# -*- coding: utf-8 -*-

from odoo import api, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.multi
    def _get_vals_for_proc_rule_subcontracting(self):
        # we change the default picking type of subcontracted service to
        # operation
        # because it's confusing for buyers to see "receive to" where
        # the production is made
        self.ensure_one()
        res = super(
            StockWarehouse, self)._get_vals_for_proc_rule_subcontracting()
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'mrp_operation'),
             ('warehouse_id', '=', self.id)
             ],
            limit=1
        )
        res['picking_type_id'] = picking_type.id
        return res
