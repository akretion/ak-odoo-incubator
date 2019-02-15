# © 2019 Akretion David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ReplaceComponent(models.TransientModel):
    _name = 'replace.component.transient'

    production_id = fields.Many2one(
        comodel_name='mrp.production', required=True,
        default=lambda s: s.env.context.get('active_id'))
    remove_product_ids = fields.Many2many(
        comodel_name='product.product', string='Products')
    remove_product_domain_ids = fields.Many2many(
        comodel_name='product.product', compute='_compute_remove_prd_domain',
        help="Only required to store domain of available removable products.")
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        domain=[('bom_line_ids', '!=', False)])
    product_uom_qty = fields.Float(string='Quantity', default=1)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom', string='Unit', readonly=True)

    @api.depends('production_id.move_raw_ids')
    def _compute_remove_prd_domain(self):
        prd_ids = [x.product_id.id for x in self.production_id.move_raw_ids]
        for rec in self:
            rec.remove_product_domain_ids = prd_ids

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
            messages.append(_("Component '%s' added" % self.product_id.name))
        self.production_id._adjust_procure_method()
        self.production_id.move_raw_ids._action_confirm()
        if messages:
            self.production_id.message_post(' - '.join(messages))
        return {'type': 'ir.actions.act_window_close'}

    def _append_raw_materials(self):
        self.ensure_one()
        routing = False
        if self.production_id.routing_id:
            routing = self.routing_id
        if routing and routing.location_id:
            source_location = routing.location_id
        else:
            source_location = self.production_id.location_src_id
        bom_line = self.env['mrp.bom.line'].search(
            [('product_id', '=', self.product_id.id)], limit=1)
        if not bom_line:
            raise UserError(
                _('Additional raw material must be defined in a bom'))
        data = {
            'sequence': 100,
            'name': self.production_id.name,
            'date': self.production_id.date_planned_start,
            'date_expected': self.production_id.date_planned_start,
            'picking_type_id': self.production_id.picking_type_id.id,
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_id.uom_id.id,
            'location_id': source_location.id,
            'location_dest_id':
                self.product_id.property_stock_production.id,
            'raw_material_production_id': self.production_id.id,
            'company_id': self.production_id.company_id.id,
            'price_unit': self.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.production_id.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.production_id.procurement_group_id.id,
            'propagate': self.production_id.propagate,
            'state': 'draft',
            # required to be consumed by produce wizard
            'bom_line_id': bom_line.id,
            # only one supported
            'unit_factor': 1,
        }
        self.env['stock.move'].create(data)

    @api.model
    def _remove_raw_materials(self):
        moves = self.env['stock.move'].search(
            [('raw_material_production_id', '=', self.production_id.id),
             ('product_id', 'in', self.remove_product_ids.ids)])
        move_lines = moves.mapped('move_line_ids')
        component_names = [x.name for x in self.remove_product_ids]
        if move_lines:
            raise UserError(_(
                "Products '%s' are not available for deletion "
                "as raw material" % component_names))
        else:
            moves._action_cancel()
            moves.unlink()
            return component_names
        return False
