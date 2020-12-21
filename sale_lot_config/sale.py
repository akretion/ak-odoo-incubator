# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien Beau <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['product.configuration.mixin', 'sale.order.line']


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def _prepare_vals_lot_number(self, order_line, index_lot):
        res = super(SaleOrder, self)._prepare_vals_lot_number(
            order_line, index_lot)
        res['config'] = order_line.config
        return res
