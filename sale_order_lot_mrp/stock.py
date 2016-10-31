# coding: utf-8
# © 2016 Florian DA COSTA @ Akretion <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_lot_vals(self, old_lot, index):
        self.ensure_one()
        lot_number = "%s-%03d" % (
            old_lot.name, index)
        return {
            'name': lot_number,
            'product_id': self.product_id.id
        }

    @api.model
    def _action_explode(self, move):
        original_lot = move.restrict_lot_id
        move_ids = super(StockMove, self.with_context(subcall=True)).\
            _action_explode(move)
        if not self.env.context.get('subcall', False) and len(move_ids) > 1 and \
                original_lot:
            lot_obj = self.env['stock.production.lot']
            index = 1
            for new_move in self.browse(move_ids):
                vals = new_move._get_lot_vals(original_lot, index)
                lot = original_lot.copy(vals)
                new_move.write({'restrict_lot_id': lot.id})
                index += 1
        return move_ids
