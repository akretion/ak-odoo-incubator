# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.modules.module import get_resource_path
from odoo.tests.common import TransactionCase


class TestAdyenImportCardRemitance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.receivable_account_id = cls.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                ),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.expense_account_id = cls.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "expense",
                ),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.bank_adyen_account = cls.env["account.account"].create(
            {
                "name": "Adyen bank account",
                "code": "511007",
                "account_type": "asset_cash",
            }
        )
        cls.adyen_journal = cls.env["account.journal"].create(
            {
                "name": "Adyen Payments",
                "type": "bank",
                "code": "ADY",
                "default_account_id": cls.bank_adyen_account.id,
                "used_for_import": True,
                "import_type": "adyen_cb_csvparser",
                "receivable_account_id": cls.receivable_account_id.id,
                "commission_account_id": cls.expense_account_id.id,
            }
        )

    def _get_import_wizard(self, filename):
        file_path = get_resource_path(
            "account_move_adyen_import", "tests/files/", filename
        )
        data = base64.b64encode(open(file_path, "rb").read())
        wizard = self.env["credit.statement.import"].create(
            {
                "journal_id": self.adyen_journal.id,
                "input_statement": data,
                "receivable_account_id": self.receivable_account_id.id,
                "commission_account_id": self.expense_account_id.id,
                "file_name": filename,
            }
        )
        return wizard

    def test_import_cb_file(self):
        wizard = self._get_import_wizard("adyen-cb.csv")
        wizard.import_statement()
        move = self.env["account.move"].search(
            [("journal_id", "=", self.adyen_journal.id)]
        )
        self.assertEqual(len(move), 1)
        self.assertEqual(len(move.line_ids), 4)
        payment_aml1 = move.line_ids.filtered(lambda line: line.name == "DEV-C262188")
        self.assertAlmostEqual(payment_aml1.credit, 258.53)
        payment_aml2 = move.line_ids.filtered(lambda line: line.name == "DEV-C262189")
        self.assertAlmostEqual(payment_aml2.credit, 26.39)
        commission_aml = move.line_ids.filtered(
            lambda line: line.account_id == self.expense_account_id
        )
        self.assertEqual(commission_aml.debit, 6.7)
        counterpart_aml = move.line_ids.filtered(
            lambda line: line.account_id == self.bank_adyen_account
        )
        self.assertEqual(counterpart_aml.debit, 278.22)
