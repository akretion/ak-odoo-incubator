# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    reserve_location_id = fields.Many2one(
        comodel_name='stock.location', string="Reserve",
        help="Location used as overstock of the picking place.")
