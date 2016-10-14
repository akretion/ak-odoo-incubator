# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    po_specific_location = fields.Many2one('stock.location')

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        res = super(ProcurementOrder, self)._prepare_orderpoint_procurement(
            orderpoint, product_qty)
        if orderpoint.location_destination_id:
            loc_id = orderpoint.location_destination_id.id
            res['po_specific_location'] = loc_id
        return res

    @api.model
    def get_merge_po_keys(self, partner, procurement):
        res = super(ProcurementOrder, self).get_merge_po_keys(
            partner, procurement)
        if procurement.orderpoint_id.location_destination_id:
            loc_id = procurement.orderpoint_id.location_destination_id.id
            additional_keys = (
                ('specific_location_id', '=', loc_id),
            )
            res += additional_keys
        return res

    @api.multi
    def _prepare_purchase_order(self, partner):
        vals = super(ProcurementOrder, self)._prepare_purchase_order(partner)
        if self.po_specific_location:
            vals['specific_location_id'] = self.po_specific_location.id
        return vals
