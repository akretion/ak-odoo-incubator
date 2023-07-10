# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _copy_data_extend_business_fields(self, values):
        if self.env.context.get("refund_mode", "") in ("refund", "cancel"):
            return
        return super()._copy_data_extend_business_fields(values)
