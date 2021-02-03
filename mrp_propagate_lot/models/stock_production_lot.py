# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    # technical fields
    phantom_lot_id = fields.Many2one(
        "stock.production.lot",
        index=True,
        copy=False,
        help="Lot that have generated this one because of bom phantom",
    )
    component_lot_ids = fields.One2many("stock.production.lot", "phantom_lot_id")
