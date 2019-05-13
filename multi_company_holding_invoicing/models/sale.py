# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    holding_company_id = fields.Many2one(
        comodel_name='res.company',
        related='agreement_id.holding_company_id',
        string=u'Holding Company for Invoicing',
        readonly=True, copy=False, store=True)
    holding_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string=u'Holding Invoice',
        copy=False, readonly=True)
    holding_invoice_state = fields.Selection([
        ('none', 'Not Applicable'),
        ('not_ready', 'Not Ready'),
        ('invoiceable', 'Invoiceable'),
        ('pending', 'Pending'),
        ('invoiced', 'Invoiced'),
    ], string=u'Holding Invoice State',
        copy=False,
        compute='_compute_holding_invoice_state',
        store=True,
        oldname='invoice_state',
        help=u"Kept for history")
    invoice_ids = fields.Many2many(store=True)
    invoice_count = fields.Integer(store=True)

    @api.multi
    @api.depends('all_qty_delivered', 'agreement_id.holding_company_id',
                 'holding_invoice_id', 'holding_invoice_id.state')
    def _compute_holding_invoice_state(self):
        for sale in self:
            if (not sale.agreement_id.holding_company_id or
                    sale.company_id == sale.agreement_id.holding_company_id):
                sale.holding_invoice_state = 'none'
            elif sale.holding_invoice_id:
                if sale.holding_invoice_id.state in ('open', 'paid'):
                    sale.holding_invoice_state = 'invoiced'
                else:
                    sale.holding_invoice_state = 'pending'
            elif sale.all_qty_delivered:
                sale.holding_invoice_state = 'invoiceable'
            else:
                sale.holding_invoice_state = 'not_ready'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        if self.env.context.get('child_invoicing'):
            for line in self:
                qty_invoiced = 0.0
                for invoice_line in line.invoice_lines.filtered(
                        lambda r: r.product_id != r.invoice_id.agreement_id.
                        holding_royalty_product_id):
                    if (invoice_line.invoice_id.state != 'cancel' and
                            invoice_line.invoice_id.type == 'out_invoice'):
                        qty_invoiced += invoice_line.uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom)
                line.qty_invoiced = qty_invoiced
        else:
            return super(SaleOrderLine, self)._get_invoice_qty()
