# © 2019 Akretion David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_assign(self):
        super(MrpProduction, self).action_assign()
        for rec in self:
            moves = rec.move_raw_ids.filtered(lambda s: not s.bom_line_id)
            moves._action_assign()
