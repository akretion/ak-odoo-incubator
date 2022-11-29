# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    # technical fields
    phantom_lot_id = fields.Many2one(
        "stock.lot",
        index=True,
        copy=False,
        help="Lot that have generated this one because of bom phantom",
    )
    component_lot_ids = fields.One2many("stock.lot", "phantom_lot_id")
    manufacturing_order_ids = fields.One2many("mrp.production", "lot_producing_id")
