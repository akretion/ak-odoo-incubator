# coding: utf-8
# © 2018 Pierrick Brun @ Akretion <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import odoo.addons.decimal_precision as dp
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price_ = fields.Float(
        string="Cout manuel",
        digits=dp.get_precision("Product Price"),
        help="Ce champ est utilisé pour le rapport de valorisation "
        "d'inventaire afin de spécifier un coût manuel",
    )
