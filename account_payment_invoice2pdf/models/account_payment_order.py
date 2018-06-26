# -*- coding: utf-8 -*-

from odoo import models, api
from PyPDF2 import PdfFileReader, PdfFileWriter
from StringIO import StringIO
import base64


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def generate_invoice_pdf(self):
        self.ensure_one()
        pdflist = []
        for payment_line in self.payment_line_ids:
            if payment_line.move_line_id.invoice_id:
                supplier_invoice = payment_line.move_line_id.invoice_id
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'account.invoice'),
                    ('res_id', '=', supplier_invoice.id),
                    ('type', '=', 'binary'),
                    ('mimetype', '=', 'application/pdf'),
                    ('company_id', '=', supplier_invoice.company_id.id)
                ], limit=1)
                pdflist.append(attachment.datas.decode('base64'))
        if pdflist:
            assembled_pdflist = self.assemble_pdf(pdflist)
            filename = '%s - %s.pdf' % (self.company_id.name, self.name)
            self.env['ir.attachment'].create({
                'name': filename,
                'datas_fname': filename,
                'type': 'binary',
                'datas': base64.encodestring(assembled_pdflist),
                'res_model': 'account.payment.order',
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })

    @api.multi
    def assemble_pdf(self, pdf_list):
        # Assemble a list of pdf
        self.ensure_one()
        output = PdfFileWriter()
        for pdf in pdf_list:
            reader = PdfFileReader(StringIO(pdf))
            for page in range(reader.getNumPages()):
                output.addPage(reader.getPage(page))
        s = StringIO()
        output.write(s)
        return s.getvalue()
