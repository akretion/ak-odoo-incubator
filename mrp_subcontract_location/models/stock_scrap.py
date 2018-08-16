# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    location_id = fields.Many2one(
        default=False)
    # because there is a race condition
    # with name get in the scrap view.
    # it will let WH/Stock instead of the result of
    # _onchange_production_id(self)
    # This bug has been fixed in v11 (js rewrite)

    @api.multi
    def do_scrap(self):
        super(StockScrap, self).do_scrap()
        # unreserve / reserve outgoing moves
        # to take in account the resulting qty of a scrap
        for rec in self:
            mo = rec.production_id
            if mo and mo.service_procurement_id:
                out_moves = [
                    move.move_dest_id
                    for move
                    in mo.move_finished_ids
                ]
                for out_move in out_moves:
                    out_move.do_unreserve()
                    out_move.action_assign()
