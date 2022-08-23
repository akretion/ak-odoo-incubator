# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import SavepointCase


class Test(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env.ref("product.product_product_8")
        cls.account_receive = cls.env.ref("account.data_account_type_receivable")
        cls.partner = cls._create_partner(cls)
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        journal = cls.env["account.journal"].search([("type", "=", "bank")], limit=1)
        cls.statement = cls.env["account.bank.statement"].create(
            {
                "name": "Test",
                "journal_id": journal.id,
            }
        )

    def test_statement(self):
        self._create_invoice(self.partner, "INV/007")
        line = self._create_statement_line(ref="INV/007")
        assert line.invoice_link[:6] == "=HYPER"
        self._create_invoice(self.partner, "INV/7")
        self._create_invoice(self.partner, "INV/42")
        line = self._create_statement_line(ref="any bla INV/7 or other INV/42 blo bli")
        assert "INV/7" in line.invoice_link
        assert "INV/42" in line.invoice_link

    def _create_statement_line(self, ref):
        vals = {
            "date": fields.Date.today(),
            "amount": 3.0,
            "payment_ref": ref,
            "statement_id": self.statement.id,
        }
        return self.env["account.bank.statement.line"].create(vals)

    def _create_partner(self):
        partner = self.env["res.partner"].create(
            {"name": "Test partner", "supplier_rank": 1, "company_type": "company"}
        )
        return partner

    def _create_invoice(self, partner, name, journal=False, move_type=False):
        if not journal:
            journal = self.journal
        if not move_type:
            move_type = "out_invoice"
        invoice = self.env["account.move"].create(
            {
                "partner_id": partner.id,
                "name": name,
                "move_type": move_type,
                "journal_id": journal.id,
            }
        )
        invoice.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "name": "test invoice line",
                            "quantity": 1.0,
                            "price_unit": 3.0,
                            "move_id": invoice.id,
                            "product_id": self.product.id,
                            "exclude_from_invoice_tab": False,
                        },
                    )
                ]
            }
        )
        return invoice
