# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_default_pricelist = fields.Boolean(
        string='Default pricelist',
        help='If checked, the pricelist is open and used by all partners'
             ' except those with a specific pricelist')
