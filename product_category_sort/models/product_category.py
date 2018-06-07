# -*- coding: utf-8 -*-
# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _parent_order = 'sequence, name'
    _order = 'parent_left'

    sequence = fields.Integer('Sequence', index=True)

    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        # TODO we should be more smart when updating the parent compute
        # in order to avoid computing and recomputing again
        if 'sequence' in vals:
            self._parent_store_compute()
        return res
