#  Copyright (C) 2015 Akretion (http://www.akretion.com).

from odoo import models
from odoo.fields import first


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _compute_journal_id(self):
        res = super()._compute_journal_id()
        allowed_journals = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("type", "in", ("bank", "cash")),
                ("available_for_manual_payment", "=", True),
            ]
        )
        for rec in self:
            if rec.journal_id not in allowed_journals:
                rec.journal_id = first(allowed_journals)
        return res
