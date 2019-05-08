# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def update_delay_from_incoming_shipment(self):
        supplier_info_obj = self.env['product.supplierinfo']
        supplierinfos = self.env['product.supplierinfo']
        for move in self:
            product = move.product_id
            supplier = move.picking_id.partner_id
            supplierinfos |= supplier_info_obj.search(
                [('name', '=', supplier.id),
                 ('product_tmpl_id', '=', product.product_tmpl_id.id),
                 '|', ('product_id', '=', product.id), 
                 ('product_id', '=', False)])
        supplierinfos._update_delay()

    def _action_done(self):
        moves = super()._action_done()
        po_moves = moves.filtered(lambda m: m.purchase_line_id)
        po_moves.update_delay_from_incoming_shipment()
