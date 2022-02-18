# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import base64
import csv
from io import StringIO

from odoo.tests.common import TransactionCase


class TestExportConfig(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_export(self):
        export = self.env["ir.exports"].create(
            {
                "name": "Test Export Partner",
                "model_id": self.env.ref("base.model_res_partner").id,
                "export_fields": [
                    (
                        0,
                        0,
                        {"name": "name", "display_name": "Partner Name", "sequence": 5},
                    ),
                    (0, 0, {"name": "email", "sequence": 3}),
                    (
                        0,
                        0,
                        {
                            "name": "country_id/code",
                            "display_name": "Country Code",
                            "sequence": 4,
                        },
                    ),
                ],
            }
        )
        export_config = self.env["ir.exports.config"].create(
            {
                "name": export.name,
                "export_id": export.id,
                "file_format": "csv",
                "additional_export_line_ids": [
                    (0, 0, {"display_name": "Static ID", "value": "ID", "sequence": 5}),
                ],
            }
        )
        azure_partner = self.env.ref("base.res_partner_12")
        attachment = export_config.get_attachment(
            azure_partner, res_id=azure_partner.id, res_model="res.partner"
        )
        self.assertEqual(len(attachment), 1)
        data = base64.b64decode(attachment.datas)
        data = data.decode()
        f = StringIO(data)
        reader = csv.reader(f, delimiter=",")
        rows = list(reader)
        self.assertEqual(len(rows), 2)
        header = rows[0]
        self.assertEqual(len(header), 4)
        self.assertEqual(header[0], "email")
        self.assertEqual(header[1], "Country Code")
        self.assertEqual(header[3], "Static ID")
        data_row = rows[1]
        self.assertEqual(data_row[0], "azure.Interior24@example.com")
        self.assertEqual(data_row[3], "ID")
