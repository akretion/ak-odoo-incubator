# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    migrated_delivery_price = fields.Float(string="Estimated Delivery Price")

    # TODO
    migrated_invoice_status = fields.Selection(
        [
            ("upselling", "Upselling Opportunity"),
            ("invoiced", "Fully Invoiced"),
            ("to invoice", "To Invoice"),
            ("no", "Nothing to Invoice"),
        ],
        string="Invoice Status",
    )
    migrated_price_done = fields.Boolean()
    migrated_invoice_state_done = fields.Boolean()

    def _set_default_value_on_column(self, cr, column_name, context=None):
        # we do not set default value as we will write real value later
        if column_name.startswith('migrated_'):
            return
        else:
            return super(SaleOrder, self)._set_default_value_on_column(
                cr, column_name, context=context)

    @api.multi
    def persist_price_fields(self, commit=False):
        total = len(self)
        for idx, record in enumerate(self):
            if commit and idx % 100 == 0:
                self._cr.commit()
                _logger.info(
                    "Commit persist price field %s / %s" % (idx, total))
            record.order_line.persist_price_fields()
            record._cr.execute("""UPDATE sale_order SET
                migrated_delivery_price=0,
                migrated_price_done=True
                WHERE id=%s""", (record.id,))

    @api.model
    def _cron_persist_price_fields(self, domain=None, limit=5000):
        if domain is None:
            domain = [
                ('state', '=', 'done'),
                ('migrated_price_done', '=', False),
                ]
        sales = self.search(
            domain, limit=limit, order='id desc')
        sales.persist_price_fields(commit=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    migrated_price_total = fields.Float()
    migrated_price_reduce = fields.Float(string="Price Reduce")
    migrated_price_tax = fields.Float(string="Taxes")
    migrated_price_subtotal = fields.Float(string="Subtotal")
    migrated_currency_id = fields.Many2one(
        related="order_id.currency_id",
        string="Currency",
        store=True
    )

    # TODO
    migrated_qty_invoiced = fields.Float(
        string="Invoiced",
        digits=dp.get_precision("Product Unit of Measure"),
        )
    migrated_qty_to_invoice = fields.Float(
        string="To Invoice",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    migrated_invoice_status = fields.Selection(
        [
            ("upselling", "Upselling Opportunity"),
            ("invoiced", "Fully Invoiced"),
            ("to invoice", "To Invoice"),
            ("no", "Nothing to Invoice"),
        ],
        string="Invoice Status",
    )

    @api.multi
    def persist_price_fields(self):
        for record in self:
            record._cr.execute("""UPDATE sale_order_line SET
                migrated_price_reduce=%s,
                migrated_price_total=%s,
                migrated_price_subtotal=%s,
                migrated_price_tax=%s
                WHERE id = %s""", (
                record.price_reduce,
                record.price_subtotal_gross,
                record.price_subtotal,
                record.price_subtotal_gross - record.price_subtotal,
                record.id))

    def _set_default_value_on_column(self, cr, column_name, context=None):
        # we do not set default value as we will write real value later
        if column_name.startswith('migrated_'):
            return
        else:
            return super(SaleOrderLine, self)._set_default_value_on_column(
                cr, column_name, context=context)
