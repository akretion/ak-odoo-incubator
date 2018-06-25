# -*- coding: utf-8 -*-

from odoo import models, api


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def generate_invoice_pdf(self):
        self.ensure_one()
        for payment_line in self.payment_line_ids:
            if payment_line.move_line_id.invoice_id:
                supplier_invoice = payment_line.move_line_id.invoice_id
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'account.invoice'),
                    ('res_id', '=', supplier_invoice.id),
                    ('type', '=', 'binary'),
                    ('company_id', '=', supplier_invoice.company_id.id)
                ], limit=1)
