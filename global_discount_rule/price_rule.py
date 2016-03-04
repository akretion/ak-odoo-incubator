# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PriceDiscountBuilder(models.Model):
    _name = 'price.discount.builder'
    _description = "Price Discount Builder"

    name = fields.Char(required=True)
    based = fields.Selection(selection=[
        ('quantity', 'Quantity'),
        ('amount', 'Amount'),
        ],
        default='quantity',
        help="")
    start_date = fields.Date(
        string='Start date',
        help="")
    end_date = fields.Date(
        string='End date',
        help="")
    percent_limit = fields.Integer(
        string="Limit (%)",
        help="Remise maximum selon montant HT de la commande")
    discount_rule_ids = fields.One2many(
        comodel_name='discount.rule', inverse_name='discount_rule_id')
    product_rule_ids = fields.One2many(
        comodel_name='product.price.rule', inverse_name='discount_rule_id')
    partner_rule_ids = fields.One2many(
        comodel_name='partner.price.rule', inverse_name='discount_rule_id')
    sequence = fields.Integer()
    active = fields.Boolean()


class DiscountRule(models.Model):
    _name = 'discount.rule'
    _description = "Price Discount Rule"

    name = fields.Char()
    qty = fields.Integer(string='Qty', required=True)
    discount = fields.Integer(required=True)
    discount_rule_id = fields.Many2one(
        comodel_name='price.discount.builder', string='Discount Builder',
        required=True, readonly=True,
        help="")
    sequence = fields.Integer()
    active = fields.Boolean()


class ProductPriceRule(models.Model):
    _name = 'product.price.rule'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product template',
        help="")
    product_id = fields.Many2one(
        comodel_name='product.product', string="Product",
        help="")
    default_code = fields.Char(help="Product code")
    categ_id = fields.Many2one(
        comodel_name='product.category', string='Category',
        help="")
    discount_rule_id = fields.Many2one(
        comodel_name='price.discount.builder', string='Discount Builder',
        required=True, readonly=True,
        help="")
    active = fields.Boolean()
    sequence = fields.Integer()


class PartnerPriceRule(models.Model):
    _name = 'partner.price.rule'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner',
        help="")
    ref = fields.Char(help="Partner code")
    discount_rule_id = fields.Many2one(
        comodel_name='price.discount.builder', string='Discount Builder',
        required=True, readonly=True,
        help="")
    active = fields.Boolean()
    sequence = fields.Integer()
