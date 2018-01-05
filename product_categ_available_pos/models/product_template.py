# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    """Trick available in pos in the search."""
    _inherit = ["categ.available_in_pos.abstract", "product.template"]
    _name = 'product.template'

    available_in_pos = fields.Boolean(
        compute='_compute_available_in_pos',
        inverse='_set_available_in_pos',
        help="Should be set from the category",
        readonly=True,
        store=False,  # because it's now company dependent
    )

    def _compute_available_in_pos(self):
        for rec in self:
            rec.available_in_pos = rec.categ_id.available_in_pos

    def _set_available_in_pos(self):
        # triggered by code only because readonly is set for view
        raise UserError("Set it from category")
