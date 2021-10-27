# Copyright 2021 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import Warning as UserError


class MassEditMoveLineAccount(models.TransientModel):
    _name = "mass.edit.move.line.account"
    _description = "Mass Edit Account"

    account_id = fields.Many2one("account.account", "Account")

    def _update_account_on_invoice(self, line):
        self.ensure_one()
        existing_lines = self.env["account.move.line"].search(
            [
                ("account_id", "=", line.account_id.id),
                ("move_id", "=", line.move_id.id),
            ]
        )
        if len(existing_lines) > 1:
            # TODO we should be able to solve that case
            # but it's harder because we do not have the link between
            # the move line and the invoice line
            # If we have only one line in the account
            # we can update all invoice line with this account without error
            raise UserError(
                _("Can not update the line as other line " "are in the same account")
            )
        else:
            invoice_lines = self.env["account.invoice.line"].search(
                [
                    ("account_id", "=", line.account_id.id),
                    ("invoice_id", "=", line.invoice.id),
                ]
            )
            invoice_lines.write({"account_id": self.account_id.id})

    def change_account(self):
        self.ensure_one()
        move_lines = self.env["account.move.line"].browse(self._context["active_ids"])
        for line in move_lines:
            if line.invoice:
                line = line.with_context(from_parent_object=True)
                self._update_account_on_invoice(line)
            line.account_id = self.account_id
        return True
