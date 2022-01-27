# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    incompatibility_location_ids = fields.One2many(
        "stock.location.transfer.incompatibility",
        "picking_type_id",
        string="Forbidden Transfers",
    )
