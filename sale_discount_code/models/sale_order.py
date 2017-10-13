# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_code = fields.Char(string='Discount code')

    @api.multi
    def clear_discount(self):
        for order in self:
            for line in order.order_line:
                if line.discount_rule_id:
                    line.write({'discount': 0, 'discount_rule_id': False})

    @api.multi
    def apply_discount(self):
        for order in self:
            if order.discount_code:
                rule = self.env['discount.code.rule'].search(
                    [('code', '=', order.discount_code)])
                if rule:
                    order.clear_discount()
                    rule._apply(order)
                else:
                    raise UserError(
                        _('Code number %s is invalid' % order.discount_code))
