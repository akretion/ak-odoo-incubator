# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    barcode = fields.Char(
        string="Code EAN",
    )
    is_edi_exportable = fields.Boolean()
