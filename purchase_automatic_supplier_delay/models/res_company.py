# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    incoming_shipment_number_delay = fields.Integer(
        default=3,
        help="Number of incoming shipment taken into account to compute "
             "the supplier delay on each product.")
