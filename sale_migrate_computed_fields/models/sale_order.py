# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    migrate_delivery_price = fields.Float(string="Estimated Delivery Price")
    migrate_invoice_status = fields.Selection(
        [
            ("upselling", "Upselling Opportunity"),
            ("invoiced", "Fully Invoiced"),
            ("to invoice", "To Invoice"),
            ("no", "Nothing to Invoice"),
        ],
        string="Invoice Status",
        default="no",
    )

    @api.multi
    def persist_computed_fields(self):
        for record in self:
            # record.migrate_delivery_price = record.delivery_price
            record.migrate_invoice_status = record.invoice_status


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    migrate_price_total = fields.Float()
    migrate_price_reduce = fields.Float(string="Price Reduce")
    migrate_qty_to_invoice = fields.Float(
        string="To Invoice",
        digits=dp.get_precision("Product Unit of Measure"),
        default=0.0,
    )
    migrate_price_tax = fields.Float(string="Taxes")
    migrate_qty_invoiced = fields.Float(
        string="Invoiced",
        digits=dp.get_precision("Product Unit of Measure"),
        default=0.0,
    )
    migrate_price_subtotal = fields.Float(string="Subtotal")
    migrate_currency_id = fields.Many2one(
        related="order_id.currency_id", string="Currency"
    )
    migrate_invoice_status = fields.Selection(
        [
            ("upselling", "Upselling Opportunity"),
            ("invoiced", "Fully Invoiced"),
            ("to invoice", "To Invoice"),
            ("no", "Nothing to Invoice"),
        ],
        string="Invoice Status",
        default="no",
    )

    @api.multi
    def persist_coomputed_fields(self):
        for record in self:
            record.migrate_price_total = record.price_total
            record.migrate_price_reduce = record.price_reduce
            record.migrate_qty_to_invoice = record.qty_to_invoice
            record.price_tax = record.price_tax
            record.migrate_qty_invoiced = record.qty_invoiced
            record.migrate_price_subtotal = record.price_subtotal
            record.migrate_currency_id = record.currency_id
            record.migrate_invoice_status = record.invoice_status
