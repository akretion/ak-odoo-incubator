# -*- coding: utf-8 -*-
# © 2018 Akretion <https://www.akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_invoice(self, order, line_ids):
        """Make sure pricelist_id is set on invoice."""
        val = super(PurchaseOrder, self)._prepare_invoice(order, line_ids)
        if order.pricelist_id:
            val.update({
                'pricelist_id': order.pricelist_id.id,
            })
        return val
