#  Copyright (C) 2021 Akretion (http://www.akretion.com).

from odoo import fields, models


class IrExportsConfig(models.Model):
    _inherit = "ir.exports.config"

    partner_edi_transport_config_ids = fields.One2many(
        "partner.export.edi",
        "edi_export_id",
        string="Partner Transport Configuration",
        help="Choose a method to send EDI files if different from the one on the supplier",
    )
