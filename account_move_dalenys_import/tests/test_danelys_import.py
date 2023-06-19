# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.modules.module import get_resource_path
from odoo.tests.common import TransactionCase


class TestPurchaseLot(TransactionCase):
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
            ],
            limit=1,
        )
        cls.bank_danelys_account = cls.env["account.account"].create(
            {
                "name": "Danelys bank account",
                "code": "512007",
                "account_type": "asset_cash",
            }
        )
        cls.danelys_journal = cls.env["account.journal"].create(
            {
                "name": "Danelys Payments",
                "type": "bank",
                "code": "DAN",
                "default_account_id": cls.bank_danelys_account.id,
                "used_for_import": True,
                "import_type": "danelys_cb_csvparser",
                "receivable_account_id": cls.receivable_account_id.id,
                "commission_account_id": cls.expense_account_id.id,
            }
        )

    def _get_import_wizard(self, filename):
        file_path = get_resource_path(
            "account_move_dalenys_import", "tests/files/", filename
        )
        data = base64.b64encode(open(file_path, "rb").read())
        wizard = self.env["credit.statement.import"].create(
            {
                "journal_id": self.danelys_journal.id,
                "input_statement": data,
                "receivable_account_id": self.receivable_account_id.id,
                "commission_account_id": self.expense_account_id.id,
                "file_name": filename,
            }
        )
        return wizard

    def test_import_cb_file(self):
        wizard = self._get_import_wizard("danelys-cb.csv")
        wizard.import_statement()
        move = self.env["account.move"].search(
            [("journal_id", "=", self.danelys_journal.id)]
        )
        self.assertEqual(len(move), 1)
        self.assertEqual(len(move.line_ids), 4)
        payment_aml1 = move.line_ids.filtered(lambda line: line.name == "SO1233")
        self.assertAlmostEqual(payment_aml1.credit, 195.67)
        commission_aml = move.line_ids.filtered(
            lambda line: line.account_id == self.expense_account_id
        )
        self.assertEqual(commission_aml.debit, 9.36)
        counterpart_aml = move.line_ids.filtered(
            lambda line: line.account_id == self.bank_danelys_account
        )
        self.assertEqual(counterpart_aml.debit, 2364.39)

    def test_paypal_import(self):
        self.danelys_journal.write({"import_type": "danelys_amex_paypal_csvparser"})
        wizard = self._get_import_wizard("danelys-paypal.csv")
        wizard.import_statement()
        moves = self.env["account.move"].search(
            [("journal_id", "=", self.danelys_journal.id)]
        )
        # multi move import
        self.assertEqual(len(moves), 2)
        self.assertEqual(len(moves[0].line_ids), 2)
        payment_aml_1 = moves.mapped("line_ids").filtered(
            lambda line: line.name == "SO431"
        )
        self.assertAlmostEqual(payment_aml_1.credit, 117.57)
