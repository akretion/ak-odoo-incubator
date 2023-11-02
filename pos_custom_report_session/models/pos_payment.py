# Copyright 2023 Akretion (https://www.akretion.com).
# @author Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PosPayment(models.Model):
    _inherit = "pos.payment"

    statement_line_id = fields.Many2one("account.bank.statement.line", "Statement Line")
