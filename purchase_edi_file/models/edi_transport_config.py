#  Copyright (C) 2021 Akretion (http://www.akretion.com).

from odoo import fields, models


class EdiTransportConfig(models.Model):
    _name = "edi.transport.config"
    _description = "edi.transport.config"

    name = fields.Char(required=True)
    edi_transfer_method = fields.Selection(
        selection=[
            ("mail", "E-mail"),
            ("external_location", "SFTP/FTP"),
            ("manual", "Manual"),
        ],
    )
    edi_storage_backend_id = fields.Many2one("fs.storage", string="FTP/SFTP Location")
    edi_mail_template_id = fields.Many2one(
        "mail.template",
        domain=[("model_id.model", "in", ("purchase.order", "res.partner"))],
        string="Edi Mail Template",
    )
