# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.queue_job.job import job
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    holding_sale_ids = fields.One2many('sale.order', 'holding_invoice_id')
    holding_sale_count = fields.Integer(
        compute='_compute_holding_sale_count',
        string='# of Sales Order',
        compute_sudo=True)
    sale_count = fields.Integer(
        compute='_compute_sale_count',
        string='# of Sales Order',
        compute_sudo=True)
    holding_invoice_id = fields.Many2one('account.invoice', 'Holding Invoice')
    child_invoice_ids = fields.One2many(
        'account.invoice', 'holding_invoice_id')
    child_invoice_count = fields.Integer(
        compute='_compute_child_invoice_count',
        string='# of Invoice',
        compute_sudo=True)
    child_invoice_job_ids = fields.One2many('queue.job', 'holding_invoice_id')
    child_invoice_job_count = fields.Integer(
        compute='_compute_child_invoice_job_count',
        string='# of Child Invoice Jobs',
        compute_sudo=True)

    def _compute_holding_sale_count(self):
        for inv in self:
            inv.holding_sale_count = len(inv.holding_sale_ids)

    def _compute_sale_count(self):
        for inv in self:
            inv.sale_count = 0
            # inv.sale_count = len(inv.sale_ids)

    def _compute_child_invoice_count(self):
        for inv in self:
            inv.child_invoice_count = len(inv.sudo().child_invoice_ids)

    def _compute_child_invoice_job_count(self):
        for inv in self:
            child_invoice_jobs = self.env['queue.job'].sudo().search([
                ('id', 'in', inv.sudo().child_invoice_job_ids.ids),
                ('state', '!=', 'done')
            ])
            inv.child_invoice_job_count = len(child_invoice_jobs)

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.holding_sale_ids and invoice.user_id.id == self.env.uid:
                invoice = invoice.suspend_security()
            invoice.holding_sale_ids._set_invoice_state('invoiced')
            super(AccountInvoice, self).invoice_validate()
        return True

    @api.multi
    def unlink(self):
        # Give some extra right to the user who have generated
        # the holding invoice
        for invoice in self:
            if invoice.holding_sale_ids and invoice.user_id.id == self.env.uid:
                invoice = invoice.suspend_security()
            sale_obj = self.env['sale.order']
            sales = sale_obj.search([('holding_invoice_id', '=', invoice.id)])
            super(AccountInvoice, invoice).unlink()
            sales._set_invoice_state('invoiceable')
        return True

    @api.multi
    def generate_child_invoice(self):
        # TODO add a group and check it
        self = self.suspend_security()
        for invoice in self:
            if invoice.child_invoice_ids:
                raise UserError(_(
                    'The child invoices have been already '
                    'generated for this invoice'))
            sale_companies = self.env['sale.order'].read_group([
                ('id', 'in', self.holding_sale_ids.ids),
                ('company_id', '!=', self.company_id.id),
            ], 'company_id', 'company_id')
            for sale_company in sale_companies:
                company_child_invoices = self.env['account.invoice'].search([
                    ('company_id', '=', sale_company['company_id'][0]),
                    ('holding_invoice_id', '=', invoice.id)
                ])
                if company_child_invoices:
                    break
                description = (
                    _('Generate child invoices for the company: %s') %
                    sale_company['company_id'][1])
                job_uuid = self.with_delay(
                    description=description).generate_child_invoice_job({
                        'company_id': sale_company['company_id'][0],
                    })
                job = self.env['queue.job'].search(
                    [('uuid', '=', job_uuid)], limit=1)
                job.write({'holding_invoice_id': invoice.id})
        return True

    @job
    @api.multi
    def generate_child_invoice_job(self, args):
        self.ensure_one()
        domain = [
            ('company_id', '=', args.get('company_id')),
            ('id', 'in', self.holding_sale_ids.ids)
        ]
        child_invoices = self.env['child.invoicing']._generate_invoice(domain)
        child_invoices.write({'holding_invoice_id': self.id})
        for child_invoice in child_invoices:
            child_invoice.signal_workflow('invoice_open')
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_line_ids = fields.Many2many(
        comodel_name='sale.order.line',
        relation='sale_order_line_invoice_rel',
        column1='invoice_id',
        column2='order_line_id')
