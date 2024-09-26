# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ScriptFileImport(models.Model):
    _name = "script.file.import"
    _description = "Script File Import"

    in_filename = fields.Char()
    out_filename = fields.Char(compute="_compute_out_filename")

    in_data = fields.Binary(string="Input CSV file", required=True)

    out_data = fields.Binary(string="Output CSV file", readonly=True)

    processor = fields.Selection(
        string="Processor", selection="_get_processor", required=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("processing", "Processing"),
            ("done", "Done"),
        ],
    )

    def _get_processor(self):
        return []

    def run_in_background(self):
        self.state = "processing"
        self.with_delay().run()

    def run(self):
        self.out_data = self.env[self.processor].run(self.in_data)
        self.state = "done"

    def _compute_out_filename(self):
        for record in self:
            record.out_filename = "Result-" + record.in_filename
