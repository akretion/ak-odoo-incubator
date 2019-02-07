# © 2019 Akretion David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ReplaceComponent(models.TransientModel):
    _name = 'replace.component.transient'

    remove_product_ids = fields.Many2many(
        comodel_name='product.product', string='Products',
        domain=lambda self: self._get_remove_product_ids_domain())
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        domain=[('bom_line_ids', '!=', False)])
    product_uom_qty = fields.Float(string='Quantity', default=1)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom', string='Unit', readonly=True)

    @api.model
    def _get_remove_product_ids_domain(self):
        res = []
        mo = self._get_manuf_order()
        if mo:
            # transient may use falsy value
            mo.invalidate_cache()
            res = [('id', 'in', [x.product_id.id for x in mo.move_raw_ids])]
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id or False

    def apply_replacement(self):
        self.ensure_one()
        messages = []
        if self.remove_product_ids:
            remove_mess = self._remove_raw_materials()
            if remove_mess:
                messages.append(_("Component %s removed" % remove_mess))
        if self.product_id:
            self._append_raw_materials()
            messages.append(_("Component %s added" % self.product_id.name))
        if messages:
            mo = self._get_manuf_order()
            mo.message_post(' - '.join(messages))
        return {'type': 'ir.actions.act_window_close'}

    def _append_raw_materials(self):
        self.ensure_one()
        mo = self._get_manuf_order()
        if mo:
            routing = False
            if mo.routing_id:
                routing = self.routing_id
            if routing and routing.location_id:
                source_location = routing.location_id
            else:
                source_location = mo.location_src_id
            bom_line = self.env['mrp.bom.line'].search(
                [('product_id', '=', self.product_id.id)], limit=1)
            if not bom_line:
                raise UserError(
                    _('Additional raw material must be defined in a bom'))
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
                'state': 'confirmed',
                # required to be consumed by produce wizard
                'bom_line_id': bom_line.id,
                # only one supported
                'unit_factor': 1,
            }
            self.env['stock.move'].create(data)

    @api.model
    def _remove_raw_materials(self):
        mo = self._get_manuf_order()
        if mo:
            moves = self.env['stock.move'].search(
                [('raw_material_production_id', '=', mo.id),
                 ('product_id', 'in', self.remove_product_ids.ids)])
            moves.write({'state': 'draft'})
            move_lines = self.env['stock.move.line'].search(
                [('move_id', 'in', moves.ids)])
            component_names = [x.name for x in self.remove_product_ids]
            if move_lines:
                raise UserError(_(
                    "Products '%s' are not available for deletion "
                    "as raw material" % component_names))
            else:
                moves.unlink()
                return component_names
        return False

    @api.model
    def _get_manuf_order(self):
        if self.env.context.get('active_model') == 'mrp.production':
            return self.env['mrp.production'].browse(
                self.env.context.get('active_id'))
        return False
