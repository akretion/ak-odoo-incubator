# coding: utf-8
# © 2017 Chafique DELLI @ Akretion <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    out_warehouse_id = fields.Many2one(
        'stock.warehouse', string='Delivery Warehouse',
        help="Default warehouse to use on Sale Orders")
    in_warehouse_id = fields.Many2one(
        'stock.warehouse', string='Reception Warehouse',
        help="Default warehouse to use on Purchase Orders")
