# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrderLinePackPrice(models.Model):
    _name = "sale.order.line.pack.price"
    _description = "Sale Order Line Pack Price"
    _rec_name = "sale_order_line_id"

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale order line",
        default=lambda self: self.env.context.get("active_id"),
    )
    currency_id = fields.Many2one(related="sale_order_line_id.currency_id")

    pack_price_catalog = fields.Monetary(
        compute="_compute_pack_price_catalog", currency_field="currency_id"
    )
    pack_price_edit = fields.Monetary(currency_field="currency_id")
    computed_discount = fields.Float(
        digits=(2, 14), compute="_compute_computed_discount"
    )

    @api.depends("sale_order_line_id")
    def _compute_pack_price_catalog(self):
        for wiz in self:
            total = 0
            if wiz.sale_order_line_id.pack_parent_line_id:
                for (
                    line
                ) in wiz.sale_order_line_id.pack_parent_line_id.pack_child_line_ids:
                    taxes = line.tax_id.compute_all(
                        line.price_unit,
                        line.order_id.currency_id,
                        line.product_uom_qty,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id,
                    )
                    total += taxes["total_excluded"]
            else:  # on the pack line itself
                for line in wiz.sale_order_line_id.pack_child_line_ids:
                    taxes = line.tax_id.compute_all(
                        line.price_unit,
                        line.order_id.currency_id,
                        line.product_uom_qty,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id,
                    )
                    total += taxes["total_excluded"]
            wiz.pack_price_catalog = total

    @api.onchange("pack_price_edit")
    def _compute_computed_discount(self):
        for wiz in self:
            if wiz.pack_price_catalog:
                wiz.computed_discount = (
                    100
                    * (wiz.pack_price_catalog - wiz.pack_price_edit)
                    / wiz.pack_price_catalog
                )
            else:
                wiz.computed_discount = 0.0

    def action_set_price(self):
        for wiz in self:
            so = wiz.sale_order_line_id.order_id
            pack_line = (
                wiz.sale_order_line_id.pack_parent_line_id or wiz.sale_order_line_id
            )
            for line in so.order_line:
                if line.pack_parent_line_id.id == pack_line.id:
                    line.discount = wiz.computed_discount
