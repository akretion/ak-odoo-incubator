# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    """Trick available in pos in the search."""
    _inherit = ["categ.available_in_pos.abstract", "product.template"]
    _name = 'product.template'

    available_in_pos = fields.Boolean(
        compute='_compute_available_in_pos',
        help="Should be set from the category",
        readonly=True,
        store=False,  # because it's now company dependent
    )

    def _compute_available_in_pos(self):
        for rec in self:
            rec.available_in_pos = rec.categ_id.available_in_pos
