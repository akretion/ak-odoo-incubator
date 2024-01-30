import base64
import io
import os
import tempfile
import zipfile

from odoo import _, api, fields, models


class InvoiceDownload(models.TransientModel):
    _name = "account.move.download"

    zip_file = fields.Binary(readonly=True)
    # seems compute won't cut it due to the lack of ctx active_ids
    # , compute="_compute_zip_file")
    file_name = fields.Char()

    # @api.depends("file_name")  # seems required to trigger once
    def _compute_zip_file(self):
        for wiz in self:
            temp_dir = tempfile.TemporaryDirectory()
            files_dir = self._prepare_files(temp_dir)
            archive = io.BytesIO()

            with zipfile.ZipFile(archive, "w") as zip_archive:
                for dirname, subdirs, filenames in os.walk(files_dir):
                    for filename in filenames:
                        file_path = os.path.join(dirname, filename)
                        zip_archive.write(file_path)

            wiz.zip_file = base64.b64encode(archive.getbuffer())
            wiz.file_name = "factures.zip"

    def create_zip_file(self):
        """
        Ideally zip content would be written on wizard init.
        But it seems hard: seems defaults don't work for file
        and seems compute doesn't work either...
        """
        self._compute_zip_file()
        return {
            "type": "ir.actions.act_window",
            "name": _("Download Invoices"),
            "view_mode": "form",
            "res_model": "account.move.download",
            "target": "new",
            "res_id": self.id,
        }

    def _prepare_files(self, temp_dir):
        active_ids = self.env.context["active_ids"]
        moves = self.env["account.move"].browse(active_ids)

        print("RECORDS", moves)

        attachments = []
        report = self.env.ref("account.account_invoices")
        for move in moves:
            report_service = report.report_name
            # result, format = b"fake content", "pdf"
            result, format = report._render_qweb_pdf([move.id])
            result = base64.b64encode(result)

            report_name = "Invoice_%s.pdf" % (move.name.replace("/", "_"))
            filename = os.path.join(temp_dir.name, report_name)
            print("writing in", filename)
            with open(filename, "wb") as file:
                file.write(result)  # TODO sure or base64?

        return temp_dir.name
