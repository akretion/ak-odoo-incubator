# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountCsvExport(models.TransientModel):
    _inherit = "account.csv.export"

    mark_exported_record = fields.Boolean(
        string="Mark Exported Entries",
        help="Prevent to export twice the same journal entries.\n"
             "Exported records are mark as exported to be exclude "
             "of the next extraction",
    )
