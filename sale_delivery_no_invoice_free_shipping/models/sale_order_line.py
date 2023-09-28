# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _is_invoiced_free_delivery(self):
        self.ensure_one()
        if (
            self.order_id.state in ("sale", "done")
            and self.is_delivery
            and not self.price_unit
        ):
            return True
        return False

    @api.depends("price_unit", "order_id.state")
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for line in self:
            if line._is_invoiced_free_delivery():
                line.invoice_status = "invoiced"
        return res

    @api.depends("price_unit", "order_id.state")
    def _compute_qty_to_invoice(self):
        res = super()._compute_qty_to_invoice()
        for line in self:
            if line._is_invoiced_free_delivery():
                line.qty_to_invoice = 0
        return res

    @api.depends("price_unit", "order_id.state")
    def _compute_qty_invoiced(self):
        res = super()._compute_qty_invoiced()
        for line in self:
            if line._is_invoiced_free_delivery():
                line.qty_invoiced = line.product_uom_qty
        return res
