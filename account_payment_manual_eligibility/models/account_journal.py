#  Copyright (C) 2015 Akretion (http://www.akretion.com).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    available_for_manual_payment = fields.Boolean(
        help="If active, the journal will be available to register a payment manually"
    )
