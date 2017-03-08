# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
# from openerp import SUPERUSER_ID


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def get_pricelist_item(self):
        for rec in self:
            origins = {}
            for line in rec.order_line:
                if line.product_id:
                    infos = rec.pricelist_id.price_rule_get(
                        line.product_id.id,
                        line.product_uom_qty, rec.partner_id.id)
                    if isinstance(infos, dict):
                        # infos i.e. {741568: {1: (239.4, 4430)}}
                        price, item = infos[infos.keys()[0]]
                        if round(line.price_unit, 2) == round(price, 2):
                            origins[line.id] = {'price_origin': item}
            o2m = [(1, k, v) for k, v in origins.items()]
            rec.write({'order_line': o2m})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_origin = fields.Many2one(
        comodel_name='product.pricelist.item', ondelete='cascade',
        help="Define which product pricelist item has been used "
             "to compute the price")

    @api.multi
    def write(self, vals):
        if 'price_origin' not in vals:
            vals['price_origin'] = False
        return super(SaleOrderLine, self).write(vals)
