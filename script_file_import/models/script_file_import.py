# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ScriptFileImport(models.Model):
    _name = "script.file.import"
    _description = "Script File Import"

    in_data = fields.Binary(string="Input CSV file", required=True)

    out_data = fields.Binary(string="Output CSV file", readonly=True)

    processor = fields.Selection(
        string="Processor", selection="_get_processor", required=True
    )

    def _get_processor(self):
        return []

    def run(self):
        selected_processor = dict(
            self._fields["processor"]._description_selection(self.env)
        ).get(self.processor)
        self.out_data = self.env[selected_processor].run(self.in_data)
