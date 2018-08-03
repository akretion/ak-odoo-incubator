# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def write(self, vals):
        result = super(StockPicking, self).write(vals)
        if 'date_done' in vals:
            for picking in self:
                if picking.sale_id:
                    sale_states = set()
                    for picking in picking.sale_id.picking_ids:
                        sale_states.add(picking.state)
                    if 'done' not in sale_states:
                        picking.sale_id.picking_state = 'unprocessed'
                    elif len(sale_states) == 1:  # values are unique
                        picking.sale_id.picking_state = 'done'
                    else:
                        picking.sale_id.picking_state = 'partially'
        return result
