# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    specific_location_id = fields.Many2one("stock.location", string="Specific Location")
    default_location_dest_id = fields.Many2one(
        related="picking_type_id.default_location_dest_id", string="Default Location"
    )

    def _get_destination_location(self):
        self.ensure_one()
        if self.specific_location_id:
            return self.specific_location_id.id
        else:
            return super()._get_destination_location()

    @api.onchange("picking_type_id")
    def onchange_specific_location(self):
        self.specific_location_id = False
