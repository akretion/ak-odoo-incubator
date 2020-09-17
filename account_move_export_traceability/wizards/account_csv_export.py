# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models, fields


class AccountCsvExport(models.TransientModel):
    _inherit = "account.csv.export"

    mark_exported_record = fields.Boolean(
        string="Mark Exported Entries",
        help="Prevent to export twice the same journal entries.\n"
        "Exported records are mark as exported to be exclude "
        "of the next extraction",
    )

    def _save_file_account_move_export(self, b64_data):
        export = self.env["account.move.export"].create(
            {
                "name": self._get_export_filename(),
                "company_id": self.company_id.id,
            }
        )
        export._create_attachment(b64_data, "account.move.export", name=export.name)
        return export

    def _get_export_filename(self):
        return _("From %s to %s extracted on %s, company %s") % (
            self.date_start,
            self.date_end,
            fields.Datetime.now(),
            self.company_id.name,
        )
