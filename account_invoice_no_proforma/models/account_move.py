# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_invoice_pdf_proforma(self):
        self.ensure_one()
        if self.state == "posted":
            report_id = self.partner_id.invoice_template_pdf_report_id or self.env.ref(
                "account.account_invoices"
            )
            report_xml_id = report_id.xml_id or "account.account_invoices"
            filename = self._get_invoice_report_filename(extension="pdf")
            content, report_type = self.env["ir.actions.report"]._pre_render_qweb_pdf(
                report_xml_id, self.ids
            )
            content_by_id = self.env["ir.actions.report"]._get_splitted_report(
                report_xml_id, content, report_type
            )
            return {
                "filename": filename,
                "filetype": "pdf",
                "content": content_by_id[self.id],
            }
        return super()._get_invoice_pdf_proforma()
