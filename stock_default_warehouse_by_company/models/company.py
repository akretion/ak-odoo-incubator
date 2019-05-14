# coding: utf-8
# © 2017 Chafique DELLI @ Akretion <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    delivery_warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Delivery Warehouse",
        help="Default warehouse to use on Sale Orders",
    )
    receipt_warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Receipt Warehouse",
        help="Default warehouse to use on Purchase Orders",
    )
