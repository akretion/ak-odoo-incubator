# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrderLinePackPrice(models.Model):
    _name = "sale.order.line.pack.price"
    _description = "Sale Order Line Pack Price"
    _rec_name = "sale_order_line_id"

    def _default_pack_price_edit(self):
        order_line = self.env["sale.order.line"].browse(
            self.env.context.get("active_id")
        )
        return self._get_pack_price_catalog(order_line)

    def _get_pack_price_catalog(self, order_line):
        if order_line.pack_parent_line_id:
            order_lines = order_line.pack_parent_line_id.pack_child_line_ids
        else:
            order_lines = order_line.pack_child_line_ids

        total = 0
        for line in order_lines:
            taxes = line.tax_id.compute_all(
                line.product_id.list_price,  # * (1 - line.discount / 100.0),
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            if line.tax_id.price_include:
                total += taxes["total_included"]
            else:
                total += taxes["total_excluded"]
        return total

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale order line",
        default=lambda self: self.env.context.get("active_id"),
    )
    currency_id = fields.Many2one(related="sale_order_line_id.currency_id")

    pack_price_catalog = fields.Monetary(
        string="Pack Price",
        compute="_compute_pack_price_catalog",
        currency_field="currency_id",
    )
    pack_price_edit = fields.Monetary(
        string="New Pack Price",
        currency_field="currency_id",
        default=_default_pack_price_edit,
    )
    computed_discount = fields.Float(
        digits=(2, 14), compute="_compute_computed_discount"
    )

    @api.depends("sale_order_line_id")
    def _compute_pack_price_catalog(self):
        for wiz in self:
            wiz.pack_price_catalog = self._get_pack_price_catalog(
                wiz.sale_order_line_id
            )

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
                    line.discount = 0  # wiz.computed_discount
                    line.price_unit = line.product_id.list_price * (
                        1 - wiz.computed_discount / 100.0
                    )
