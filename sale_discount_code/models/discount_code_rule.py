# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError


class DiscountCodeRule(models.Model):
    _name = 'discount.code.rule'
    _description = 'Discount Code Rule'

    sequence = fields.Integer('Sequence', default=10)
    application_type = fields.Selection(
        selection=[('manual', 'Manual')], string='Application type',
        default='manual')
    code = fields.Char('Code')
    discount_amount = fields.Float(
        string='Discount amount',
        digits_compute=dp.get_precision('Account'),
        required=True)
    date_from = fields.Date()
    date_to = fields.Date()
    restriction_method = fields.Selection(
        selection=[
            ('no_restriction', 'No restriction'),
            ('partner_list', 'Partner list'),
            ('newsletter', 'Only newsletter'),
            ('pricelist', 'Pricelist')],
        string="Restriction method")
    restrict_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='discount_rule_partner_rel',
        column1='rule_id',
        column2='partner_id',
        string='Restricted partners')
    restrict_pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        relation='discount_rule_pricelist_rel',
        column1='rule_id',
        column2='pricelist_id',
        string='Restricted pricelists')
    usage_restriction = fields.Selection(
        selection=[
            ('one_per_partner', 'One per partner'),
            ('no_restriction', 'No restriction')])
    restriction_amount = fields.Selection(
        selection=[
            ('taxed_amount', 'Taxed amount'),
            ('untaxed_amount', 'Untaxed amount')])
    minimal_amount = fields.Float(
        string='Minimal amount',
        digits_compute=dp.get_precision('Account'))

    _sql_constraints = [
        ('code_unique', 'UNIQUE (code)', _('Discount code must be unique !'))]

    @api.model
    def _check_restriction_partner_list(self, order):
        return order.partner_id.id not in self.restrict_partner_ids.ids

    @api.model
    def _check_restriction_pricelist(self, order):
        return order.pricelist_id.id not in self.restrict_pricelist_ids.ids

    @api.model
    def _check_restriction_newsletter(self, order):
        return order.partner_id.opt_out

    @api.model
    def _check_apply(self, order):
        if (self.date_to and fields.Date.today() > self.date_to) \
                or (self.date_from and fields.Date.today() < self.date_from):
            return False
        if self.minimal_amount and (
                (self.restriction_amount == 'taxed_amount' and \
                    self.minimal_amount > order.amount_total) \
                or (self.restriction_amount == 'untaxed_amount' and \
                self.minimal_amount > order.amount_untaxed)):
            return False
        restriction_func = '_check_restriction_%s' % self.restriction_method
        if restriction_func():
            return False
        if self.usage_restriction == 'one_per_partner':
            lines = self.env['sale.order.line'].search([
                ('order_id', '!=', order.id),
                ('discount_rule_id', '=', self.id),
                ('state', '!=', 'cancel')])
            if lines:
                return False
        return True

    @api.model
    def _apply_discount(self, order):
        self.ensure_one()
        for line in order.order_line:
            if not line.discount_rule_id:
                line.write({
                    'discount': self.discount_amount,
                    'discount_rule_id': self.id})

    @api.model
    def _apply(self, order):
        for line in order.order_line:
            if line.discount_rule_id:
                line.write({'discount': 0, 'discount_rule_id': False})
        if self._check_apply(order):
            self._apply_discount(order)
        else:
            raise UserError(
                _('The rule %s cannot be applied on the sale order %s' % (
                    self.code, order.name)))
