# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        for move in self:
            move.check_location_compatible()
        return super(StockMove, self).action_done()

    @api.multi
    def check_location_compatible(self):
        for move in self:
            picking_type = move.picking_id.picking_type_id or move.picking_type_id
            if not picking_type:
                continue
            forbidden = False
            for location_rule in picking_type.incompatibility_location_ids:
                check = False
                if move.location_id.belongs_to(location_rule.location1_id):
                    check = "loc_2"
                elif move.location_id.belongs_to(location_rule.location2_id):
                    check = "loc_1"
                if check:
                    if check == "loc_1" and move.location_dest_id.belongs_to(
                        location_rule.location1_id
                    ):
                        forbidden = True
                    elif check == "loc_2" and move.location_dest_id.belongs_to(
                        location_rule.location2_id
                    ):
                        forbidden = True
                if forbidden:
                    raise UserError(
                        _(
                            "Tranfer between %s and %s is not allowed for %s picking "
                            "type"
                        )
                        % (
                            location_rule.location1_id.name,
                            location_rule.location2_id.name,
                            location_rule.picking_type_id.display_name,
                        )
                    )
