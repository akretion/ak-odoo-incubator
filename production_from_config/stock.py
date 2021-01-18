# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien Beau <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    config = fields.Serialized(
        "Configuration", readonly=True, help="Allow to set custom configuration"
    )
