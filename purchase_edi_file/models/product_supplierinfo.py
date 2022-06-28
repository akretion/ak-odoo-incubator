#  Copyright (C) 2021 Akretion (http://www.akretion.com).

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    purchase_edi_id = fields.Many2one(
        "ir.exports.config",
        "Edi Profile",
        domain=[("resource", "=", "purchase.order.line")],
    )
