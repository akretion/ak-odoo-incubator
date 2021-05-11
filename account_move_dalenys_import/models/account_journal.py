# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_type = fields.Selection(
        selection_add=[
            ('be2bill_cb_csvparser',
             'Be2bill CB .csv'),
            ('be2bill_amex_paypal_csvparser',
             'be2bill American Express/Paypal .csv'),
        ])
