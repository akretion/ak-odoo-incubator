# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        return super(
            AccountMoveReversal, self.with_context(refund_mode=self.refund_method)
        ).reverse_moves()
