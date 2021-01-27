# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_raw_material_from_config(self, original_moves_vals):
        self.ensure_one()
        return original_moves_vals

    def _get_moves_raw_values(self):
        moves_vals = super()._get_moves_raw_values()
        production_move_vals = {}
        for move_vals in moves_vals:
            production_id = move_vals["raw_material_production_id"]
            if production_id not in production_move_vals:
                production_move_vals[production_id] = []
            production_move_vals[production_id].append(move_vals)

        final_moves_vals = []

        for production, prod_moves_vals in production_move_vals:
            final_prod_moves_vals = production._get_raw_material_from_config(
                prod_moves_vals
            )
            final_moves_vals += final_prod_moves_vals
        return final_moves_vals
