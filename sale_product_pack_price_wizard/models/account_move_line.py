# Copyright 2024 Akretion - Raphaël Valyi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    price_unit = fields.Float(
        digits="Line Item Price",
    )
