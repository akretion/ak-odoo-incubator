# -*- coding: utf-8 -*-

from odoo import models, api
import base64


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def generate_invoice_pdf(self):
        self.ensure_one()
        pdfdocuments = []
        for payment_line in self.payment_line_ids:
            if payment_line.move_line_id.invoice_id:
                supplier_invoice = payment_line.move_line_id.invoice_id
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'account.invoice'),
                    ('res_id', '=', supplier_invoice.id),
                    ('type', '=', 'binary'),
                    ('company_id', '=', supplier_invoice.company_id.id)
                ], limit=1)
                pdfdocuments.append(attachment)
        if pdfdocuments:
            merged_pdfdocument = self.env['report']._merge_pdf(pdfdocuments)
            filename = '%s - %s.pdf' % (self.company_id.name, self.name)
            self.env['ir.attachment'].create({
                'name': filename,
                'datas_fname': filename,
                'type': 'binary',
                'datas': base64.encodestring(merged_pdfdocument),
                'res_model': 'account.payment.order',
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })
