# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def product_id_change(
            self, cr, uid, ids, pricelist, product_id, *args, **kwargs):
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product_id, *args, **kwargs)
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id)
            res['value']['discount'] = int(product.discount)
        else:
            res['value']['discount'] = 0
        return res
