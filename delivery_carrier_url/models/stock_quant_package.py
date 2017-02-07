# -*- coding: utf-8 -*-
#  Copyright (C) 2017 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    @api.model
    def _get_tracking_url(self, picking):
        """
        Override this method for your carrier
        """
        pass

    @api.multi
    @api.returns('stock.picking')
    def _get_picking_from_package(self):
        operation_obj = self.env['stock.pack.operation']
        if self._context.get('picking_id', False):
            picking = self.env['stock.picking'].browse(
                self._context['picking_id'])
        else:
            picking_type = self.env.ref('stock.picking_type_out')
            operations = operation_obj.search(
                ['|',
                 ('package_id', '=', self.id),
                 ('result_package_id', '=', self.id),
                 ('picking_id.picking_type_id', '=', picking_type.id)]
            )
            pickings = self.env['stock.picking'].browse()
            for operation in operations:
                pickings |= operation.picking_id
            picking = pickings[0]
        return picking

    @api.multi
    def open_tracking_url(self):
        self.ensure_one()
        picking = self._get_picking_from_package()
        tracking_url = self._get_tracking_url(picking)
        if not tracking_url:
            raise UserError(
                _('No tracking url for the carrier %s.'
                  % picking.carrier_id.name))
        client_action = {
            'type': 'ir.actions.act_url',
            'name': "Shipment Tracking Page",
            'target': 'new',
            'url': tracking_url,
        }
        return client_action
