# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_item_id = fields.Many2one(
        comodel_name='product.pricelist.item', string="Price Origin",
        compute='_compute_price_item', store=True,
        readonly=True, ondelete='set null',
        help="Define which product pricelist item has been used "
             "to compute the price unit")

    @api.multi
    @api.depends('product_id', 'price_unit')
    def _compute_price_item(self):
        """ According to price update, compute rule which brings the price
        """
        for line in self:
            if line.product_id:
                infos = line.order_id.pricelist_id.price_rule_get(
                    line.product_id.id, line.product_uom_qty,
                    line.order_id.partner_id.id)
                if isinstance(infos, dict):
                    # infos i.e. {1: (239.4, 4430)}
                    price, item = infos[infos.keys()[0]]
                    if round(line.price_unit, 2) == round(price, 2):
                        line.pricelist_item_id = item
