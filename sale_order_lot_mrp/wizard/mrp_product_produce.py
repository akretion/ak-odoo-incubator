# coding: utf-8
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class MrpProductProduct(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.model
    def _get_default_lot(self):
        prod_id = self.env.context['active_id']
        prod = self.env['mrp.production'].browse(prod_id)
        return prod.lot_id.id

    lot_id = fields.Many2one('stock.production.lot', 'Lot',
                             default=_get_default_lot)
