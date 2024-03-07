# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_type = fields.Selection(
        selection_add=[
            ("adyen_cb_csvparser", "Adyen Credit Card .csv"),
            ("adyen_multi_move_csvparser", "Adyen Multiple Entries .csv"),
        ]
    )

    def _get_global_commission_amount(self, parser):
        global_commission_amount = super()._get_global_commission_amount(parser)
        if hasattr(parser, "extra_commission"):
            extra_commission = (
                parser.commission_sign == "+"
                and -parser.extra_commission
                or parser.extra_commission
            )
            global_commission_amount += extra_commission
        return global_commission_amount
