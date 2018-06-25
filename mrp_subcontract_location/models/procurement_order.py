# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def run(self, autocommit=False):
        res = super(ProcurementOrder, self).run(autocommit=autocommit)
        # Copied from stock/models/procurement.py but for out now action
        # TODO maybe it is best not implementing new action, but just a new parameter and use context or something
        move_ids = self.filtered(lambda order: order.state == 'running' and order.rule_id.action == 'move_default_supplier_src').mapped('move_ids').filtered(lambda move: move.state == 'draft')
        if move_ids:
            move_ids.action_confirm()
        return res

    @api.multi
    def _run(self):
        if self.rule_id.action == 'move_default_supplier_src':
            # TODO decide what we do with service product, which product  carry supplier, etc...
            prod = self.product_id.bom_ids.service_id
            if not prod:
                self.message_post(body=_('configuration problem'))
                return False
            supplier = (prod.seller_ids and
                        prod.seller_ids[0] or False)
            if not supplier or not supplier.name.manufacture_location_id:
                self.message_post(body=_('No supplier location defined'))
                return False
            location = supplier.name.manufacture_location_id
            supp_wh = location.get_warehouse()
            supp_vals = {
                'location_id': location.id,
                'warehouse_id': supp_wh.id,
                # Avoid picking creation
                'picking_type_id': False
            }
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            self.env['stock.move'].sudo().create(self.with_context(supp_vals=supp_vals)._get_stock_move_values())
            return True
        return super(ProcurementOrder, self)._run()

    def _get_stock_move_values(self):
        vals = super(ProcurementOrder, self)._get_stock_move_values()
        if self.env.context.get('supp_vals'):
            vals.update(self.env.context.get('supp_vals'))
        return vals
