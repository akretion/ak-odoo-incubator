# Copyright 2023 Akretion
# @author Francois Poizat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    zebra_printer_host = fields.Char(
        string="Printer host url",
        help="The Url of the printer onto which the barcode will be printer",
        default="https://localhost",
        config_parameter="label_printer_poc.zebra_printer_host"
    )

    zebra_printer_name = fields.Char(
        string="Printer name",
        help="The name of the printer onto which the barcode will be printer",
        default="zebra_large",
        config_parameter="label_printer_poc.zebra_printer_name"
    )
