# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    available_in_pos = fields.Boolean(
        sting="Available in POS",
        help="Toggle visiblity in Point of sale",
        company_dependent=True,
    )

    available_in_pos_view = fields.Boolean(
        # only for the form view : force the use of compute
        string="This category and its products are visible in Point of sale",
        name="Available in POS",
        help="Switching this will impact all children categories.",
        compute="_compute_available_in_pos_view",
        inverse="_inverse_available_in_pos_view",
        store=False,
    )

    def _compute_available_in_pos_view(self):
        for rec in self:
            rec.available_in_pos_view = rec.available_in_pos

    def _inverse_available_in_pos_view(self):
        for rec in self:
            rec.set_available_in_pos(rec.available_in_pos_view)

    @api.model
    def get_parents_category_domain(self, arg):
        return [("child_id", "parent_of", arg)]

    @api.model
    def get_children_category_domain(self, arg):
        return [("parent_id", "child_of", arg)]

    @api.multi
    def set_available_in_pos(self, active):
        """Toggle available_in_pos for the current company.

        In pos, category tree can't contain gaps:
        "All/Seleable" can't be displayed if his parent
        "All" is not available.

        @params: active (boolean)
            if true, will set available_in_pos flag to
            this category and its parents.
            if false, will unset available_in_pos flag to
            this category and its children.
        """
        self.ensure_one()
        if active:
            get_domain = self.get_parents_category_domain
        else:
            get_domain = self.get_children_category_domain
        categs = self.search(get_domain(self.id))
        categs.write({"available_in_pos": active})
