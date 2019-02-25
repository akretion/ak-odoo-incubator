# -*- coding: utf-8 -*-

from odoo import api, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # As we handle subcontractor, warehouse may belong to a supplier but we
    # may buy classic products to these supplier and need the normal supplier
    # location on supplier, not the transit location.
    # TODO handle case if partner is supplier or not?
    @api.model
    def _update_partner_data(self, partner_id, company_id):
        return
#        if partner_id:
#            partner = self.env['res.partner'].browse(partner_id)
#            if partner.supplier:
#                return
#        return super(StockWarehouse, self)._update_partner_data(
#            partner_id, company_id)

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
