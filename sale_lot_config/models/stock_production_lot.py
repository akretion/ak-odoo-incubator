# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    config = fields.Serialized(
        "Configuration", readonly=True, help="Allow to set custom configuration"
    )
