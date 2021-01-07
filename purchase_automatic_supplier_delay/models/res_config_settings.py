# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    incoming_shipment_number_delay = fields.Integer(
        string="Incoming Shipment Number Delay",
        related="company_id.incoming_shipment_number_delay",
        readonly=False,
        help="Number of incoming shipment taken into account to compute "
        "the supplier delay on each product.",
    )
