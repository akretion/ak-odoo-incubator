# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Backport is part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    def _add_precomputed_values(self, vals_list):
        """PARTIAL BACKPORT FROM ODOO 16

        It backports the precompute feature on create but does not
        do all sanity checks that are done in Odoo 16.
        It does not work with inverse fields yet.

        --

        Add missing precomputed fields to ``vals_list`` values.
        Only applies for precompute=True fields.

        :param dict vals_list: list(dict) of create values
        """
        precomputable = {
            fname: field
            for fname, field in self._fields.items()
            if getattr(field, "precompute", False) and not field.inverse
        }
        if not precomputable:
            return

        # determine which vals must be completed
        vals_list_todo = [
            vals
            for vals in vals_list
            if any(fname not in vals for fname in precomputable)
        ]
        if not vals_list_todo:
            return

        # create new records for the vals that must be completed
        records = self.browse().concat(*(self.new(vals) for vals in vals_list_todo))

        for record, vals in zip(records, vals_list_todo):
            for fname, field in precomputable.items():
                if fname not in vals:
                    # computed stored fields with a column
                    # have to be computed before create
                    # s.t. required and constraints can be applied on those fields.
                    vals[fname] = field.convert_to_write(record[fname], self)

    @api.model_create_multi
    def create(self, vals_list):
        self._add_precomputed_values(vals_list)
        return super().create(vals_list)
