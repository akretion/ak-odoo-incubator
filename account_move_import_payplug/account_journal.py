# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_type = fields.Selection(
        selection_add=[("payplug_csvparser", "Parser for payplug import statement")],
        ondelete={"payplug_csvparser": "set default"},
    )
