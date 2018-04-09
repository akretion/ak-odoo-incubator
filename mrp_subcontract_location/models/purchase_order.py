# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    warehouse_id = fields.Many2one(related='picking_type_id.warehouse_id',
        string='Warehouse',
        help="Technical field used to display the Drop Ship Address",
        readonly=True)

    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        for purchase in self:
            for line in purchase.order_line:
                if line._is_service_procurement():
                    mo = line.procurement_ids.production_id
                    mo.update_locations(purchase)

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        supplier_wh = self.env.ref(
            'mrp_subcontract_location.warehouse_supplier')
        if supplier_wh.id == self.warehouse_id.id and self.dest_address_id:
            if not self.partner_id.supplier_location_id:
                raise exceptions.ValidationError(
                    _('No location configured on the subcontractor'))
            return self.dest_address_id.supplier_location_id.id
        else:
            return super(PurchaseOrder, self)._get_destination_location()
