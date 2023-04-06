# Copyright 2023 Akretion
# @author Francois Poizat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    zebra_printer_host = fields.Char(
        string="Printer host url",
        help="The Url of the printer onto which the barcode will be printer",
        default="https://localhost",
        config_parameter="label_printer_poc.zebra_printer_host"
    )

    @api.constrains('zebra_printer_host')
    def _host_validation(self):
        for record in self:
            regex = re.compile(
                    r'^(?:http)s?://' # http:// or https://
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                    r'localhost|' #localhost...
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                    r'(?::\d+)?' # optional port
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if (regex.match(record.zebra_printer_host) is None):
                raise ValidationError('Barcode: Printer host url Must be a valid url')


    zebra_printer_port = fields.Integer(
        string="Printer host port",
        help="The port of the printer onto which the barcode will be printer",
        default="443",
        config_parameter="label_printer_poc.zebra_printer_port"
    )

    zebra_printer_name = fields.Char(
        string="Printer name",
        help="The name of the printer onto which the barcode will be printer",
        default="zebra_large",
        config_parameter="label_printer_poc.zebra_printer_name")
