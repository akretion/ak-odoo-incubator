# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductSupplierinfo(models.Model):
    _inherit = ["product.supplierinfo", "product.supplierinfo.attr.mixin"]
    _name = "product.supplierinfo"
