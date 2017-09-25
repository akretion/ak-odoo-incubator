# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_rule_id = fields.Many2one(
        comodel_name='discount.code.rule', string='Discount code')
