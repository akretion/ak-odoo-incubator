# coding: utf-8
# © 2015 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    warning_time = fields.Float(
        string="Warning time",
        default=2.0,
        help="The warning time (in days) before that the requested date"
        " indicated on the delivery order expires.",
    )
