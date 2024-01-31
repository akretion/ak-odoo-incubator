#  Copyright (C) 2021 Akretion (http://www.akretion.com).

from odoo import fields, models


class PartnerExportEdi(models.Model):
    _name = "partner.export.edi"
    _description = "Link between EDI exports config partner and transport edi config"

    partner_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        required=True,
        domain="[('edi_transport_config_id', '!=', False)]",
    )
    edi_transport_config_id = fields.Many2one(
        "edi.transport.config", required=True, string="EDI Transport Configuration"
    )
    edi_export_id = fields.Many2one("ir.exports.config", required=True)
