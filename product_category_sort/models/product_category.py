# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.multi
    def write(self, vals):
        super(ProductCategory, self).write(vals)
        # TODO we should be more smart when updating the parent compute
        # in order to avoid computing and recomputing again
        if 'sequence' in vals:
            self._parent_store_compute()
        return True
