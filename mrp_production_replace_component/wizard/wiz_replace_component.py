# © 2019 Akretion David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ReplaceComponent(models.TransientModel):
    _name = 'replace.component.transient'

    remove_product_ids = fields.Many2many(
        comodel_name='product.product', string='Products', required=True,
        domain=lambda self: self._get_remove_product_ids_domain())
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        domain=[('type', 'in', ['consu', 'product'])])
    product_uom_qty = fields.Float(string='Quantity', default=1)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom', string='Unit', readonly=True)

    @api.model
    def _get_remove_product_ids_domain(self):
        res = [('id', '=', 0)]
        mo = self.env['mrp.production'].browse(
            self.env.context.get('active_id'))
        if mo:
            res = [('id', 'in', [x.product_id.id for x in mo.move_raw_ids])]
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id or False

    def apply_replacement(self):
        self.ensure_one()
        self._remove_raw_materials(self.remove_product_ids)
        self._append_raw_materials()

    def _append_raw_materials(self):
        self.ensure_one()
        mo_id = self._guess_mo_id()
        if mo_id:
            mo = self.env['mrp.production'].browse(mo_id)
            routing = False
            if mo.routing_id:
                routing = self.routing_id
            if routing and routing.location_id:
                source_location = routing.location_id
            else:
                source_location = mo.location_src_id
            data = {
                'sequence': 100,
                'name': mo.name,
                'date': mo.date_planned_start,
                'date_expected': mo.date_planned_start,
                'picking_type_id': mo.picking_type_id.id,
                'product_id': self.product_id.id,
                'product_uom_qty': self.product_uom_qty,
                'product_uom': self.product_id.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id':
                    self.product_id.property_stock_production.id,
                'raw_material_production_id': mo.id,
                'company_id': mo.company_id.id,
                'price_unit': self.product_id.standard_price,
                'procure_method': 'make_to_stock',
                'origin': mo.name,
                'warehouse_id': source_location.get_warehouse().id,
                'group_id': mo.procurement_group_id.id,
                'propagate': mo.propagate,
                'unit_factor': 1,
            }
            self.env['stock.move'].create(data)

    @api.model
    def _remove_raw_materials(self, products):
        mo_id = self._guess_mo_id()
        if mo_id:
            moves = self.env['stock.move'].search(
                [('raw_material_production_id', '=', mo_id),
                 ('product_id', 'in', products.ids)])
            move_lines = self.env['stock.move.line'].search(
                [('move_id', 'in', moves.ids)])
            if move_lines:
                raise UserError(_(
                    "Products '%s' are not available for deletion "
                    "as raw material" % [x.name for x in products]))

    @api.model
    def _guess_mo_id(self):
        if self.env.context.get('active_model') != 'mrp.production':
            raise UserError(
                _("Replace Component:\n\n"
                  "Active model must be 'mrp.production' instead of '%s'"
                  % self.env.context.get('active_model')))
        return self.env.context.get('active_id')
