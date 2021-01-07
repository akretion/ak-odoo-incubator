# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        incoming_picks = self.filtered(lambda p: p.picking_type_id.code == "incoming")
        incoming_picks.mapped("move_lines").update_delay_from_incoming_shipment()
        return res
