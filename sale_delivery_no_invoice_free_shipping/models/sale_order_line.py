# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("price_unit")
    def _compute_invoice_status(self):
        super()._compute_invoice_status()
        for line in self:
            if line.is_delivery and not line.price_unit:
                line.invoice_status = "invoiced"

    @api.depends("price_unit")
    def _get_to_invoice_qty(self):
        super()._get_to_invoice_qty()
        for line in self:
            if line.is_delivery and not line.price_unit:
                line.qty_to_invoice = 0

    @api.depends("price_unit")
    def _get_invoice_qty(self):
        super()._get_invoice_qty()
        for line in self:
            if line.is_delivery and not line.price_unit:
                line.qty_invoiced = line.product_uom_qty
