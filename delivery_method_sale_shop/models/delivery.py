# coding: utf-8
# © 2014 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class DeliveryMethod(models.Model):
    _inherit = 'delivery.carrier'

    shop_method = fields.Many2many(
        comodel_name='sale.shop.method',
        inverse_name='delivery_methods')


class Keychain(models.Model):
    _inherit = 'keychain.account'

    shop_methods = fields.One2many(
        comodel_name='sale.shop.method',
        inverse_name='keychain')


class SaleShop(models.Model):
    _inherit = 'sale.shop'

    shop_methods = fields.One2many(
        comodel_name='sale.shop.method',
        inverse_name='shop'
    )
    shipping_sender_id = fields.Many2one(
        'res.partner', string='Shipping Sender',
        help='Sender address. The main partner will be used if this field '
             'is empty.'
    )


class ShopMethod(models.Model):
    _name = 'sale.shop.method'
    # associe un keychain à une méthode à un shop

    # faire un inherit ?
    # on pointe vers 1 seul shop
    shop = fields.Many2one(
        comodel_name='sale.shop',
        inverse_name='shop_methods')

    # on pointe vers plusieurs méthodes de livraions
    delivery_methods = fields.Many2many(
        comodel_name='delivery.carrier',
        inverse_name='shop_methods')

    keychain = fields.Many2one(
        comodel_name='keychain.account',
        inverse_name='shop_methods')


