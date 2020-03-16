# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    # TODO is this going to obliterate performance at startup?
    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._model_id.gtl_refresh_record_rules()
        return res

    def write(self, vals):
        res = super().write(vals)
        res._model_id.gtl_refresh_record_rules()
        return res

    def unlink(self):
        return super().unlink()
        res._model_id.gtl_refresh_record_rules()
