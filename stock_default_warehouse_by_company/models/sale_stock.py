# coding: utf-8
# © 2017 Chafique DELLI @ Akretion <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_default_warehouse(self):
        company = self.env.user.company_id
        if company.delivery_warehouse_id:
            return company.delivery_warehouse_id.id
        return super(SaleOrder, self)._get_default_warehouse()

    warehouse_id = fields.Many2one(default=_get_default_warehouse)
