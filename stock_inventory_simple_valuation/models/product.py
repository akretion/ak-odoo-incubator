# coding: utf-8
# © 2018 Pierrick Brun @ Akretion <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import odoo.addons.decimal_precision as dp
from odoo import api, models, fields, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    standard_price_ = fields.Float(digits=dp.get_precision('Product Price'))

