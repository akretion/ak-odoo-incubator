# coding: utf-8
# © 2017 Chafique DELLI @ Akretion <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_picking_in(self):
        company = self.env.user.company_id
        if company.reception_warehouse_id:
            types = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'),
                ('warehouse_id', '=', company.reception_warehouse_id.id)])
            if types:
                return types[0]
        return super(PurchaseOrder, self)._get_picking_in()

    picking_type_id = fields.Many2one(default=_get_picking_in)
