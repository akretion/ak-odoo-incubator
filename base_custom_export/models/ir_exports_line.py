#  Copyright (C) 2015 Akretion (http://www.akretion.com).

from odoo import fields, models


class IrExportsLine(models.Model):
    _inherit = "ir.exports.line"

    field_description = fields.Char()
