# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    delivery_delay = fields.Integer(
        string="Delivery Delay",
        help="This delay will be used to calculate the planned date on "
        "incoming shipment if there is not historic for a product",
    )
