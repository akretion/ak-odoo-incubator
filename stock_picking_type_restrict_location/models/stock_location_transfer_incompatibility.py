# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import fields, models


class StockLocationTransferIncompatibility(models.Model):
    _name = "stock.location.transfer.incompatibility"
    _description = "Prevent transfer between 2 locations for picking types"

    picking_type_id = fields.Many2one(
        "stock.picking.type", string="Picking Type", required=True
    )
    location1_id = fields.Many2one(
        "stock.location", string="Source Location", required=True
    )
    location2_id = fields.Many2one(
        "stock.location", string="Destination Location", required=True
    )
