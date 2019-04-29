# coding: utf-8
# © 2017 Chafique DELLI @ Akretion <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseOrder, self).default_get(fields_list)
        company = self.env.user.company_id
        if company.receipt_warehouse_id:
            picking_types = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'),
                ('warehouse_id', '=', company.receipt_warehouse_id.id)])
            if picking_types:
                res['picking_type_id'] = picking_types[0].id
        return res
