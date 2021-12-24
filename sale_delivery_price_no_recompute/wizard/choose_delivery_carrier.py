# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = "choose.delivery.carrier"

    @api.onchange("carrier_id")
    def _onchange_carrier_id(self):
        return {}

    @api.onchange("order_id")
    def _onchange_order_id(self):
        return {}
