# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_type = fields.Selection(
        selection_add=[
            ("danelys_cb_csvparser", "Danelys CB .csv"),
            ("danelys_amex_paypal_csvparser", "Danelys American Express/Paypal .csv"),
        ]
    )
