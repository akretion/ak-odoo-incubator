# Copyright 2023 Akretion
# @author Francois Poizat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    printer_host = fields.Char(
        string="Printers host url",
        help="The Url of the printer server",
        default="https://localhost:443",
        config_parameter="label_printer_poc.zebra_printer_host"
    )

    @api.constrains('printer_host')
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

    product_label_printer_name = fields.Char(
        string="Product label printer name",
        help="The name of the printer onto which the product label will be printed",
        default="zebra_large",
        config_parameter="label_printer_poc.zebra_printer_name")

    shipping_label_printer_name = fields.Char(
        string="Shipping label printer name",
        help="The name of the printer onto which the shipping label will be printed",
        default="zebra_large",
        config_parameter="label_printer_poc.zebra_printer_name")

    a4_printer_name = fields.Char(
        string="Printer name",
        help="The name of the printer onto which a4 document will be printed",
        default="printer",
        config_parameter="label_printer_poc.zebra_printer_name")
