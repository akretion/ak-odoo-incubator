# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange("product_id")
    def product_id_change(self):
        self._add_pricelist_in_context()
        return super(SaleOrderLine, self).product_id_change()

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        self._add_pricelist_in_context()
        return super(SaleOrderLine, self).product_uom_change()

    def _add_pricelist_in_context(self):
        # Sadly you can not use with_context in onchange
        # If you use it, all change are apply in the new env
        # and so at the end of the onchange the original env didn't change
        # and no onchange have been applyed
        ctx = self.env.context.copy()
        ctx["pricelist_id"] = self.order_id.pricelist_id.id
        self.env.context = ctx
