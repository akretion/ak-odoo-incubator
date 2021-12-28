# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import Warning as UserError


class MassEditMoveLineAccount(models.TransientModel):
    _name = "mass.edit.move.line.account"
    _description = "Mass Edit Account"

    account_id = fields.Many2one("account.account", "Account")

    def change_account(self):
        self.ensure_one()
        move_lines = self.env["account.move.line"].browse(self._context["active_ids"])
        for line in move_lines:
            lock_dt = line.company_id.fiscalyear_lock_date
            if lock_dt and lock_dt >= line.date:
                raise UserError(_("You can not update locked move"))
            line.account_id = self.account_id
        return True
