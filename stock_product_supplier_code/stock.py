# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields

import logging
logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_supplier_code = fields.Char(
        string='Supplier Code', compute='_compute_supplier_code',
        store=True, readonly=True,
        help="Supplier product code if Partner is the supplier")

    @api.multi
    @api.depends('product_id', 'picking_id.partner_id')
    def _compute_supplier_code(self):
        for rec in self:
            supplier_code = False
            if rec.picking_id.partner_id and rec.product_id:
                for supplier_info in rec.product_id.seller_ids:
                    if supplier_info.name == rec.picking_id.partner_id:
                        supplier_code = supplier_info.product_code
            rec.product_supplier_code = supplier_code
