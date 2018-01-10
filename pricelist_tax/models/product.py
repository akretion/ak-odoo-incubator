# coding: utf-8
# © 2017  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    price_include_taxes = fields.Boolean(
        string=u"Prix en TTC",
        help=u"Si coché les prix de cette liste de prix doivent être en TTC\n"
             u"sinon en HT.\n")

    @api.multi
    @api.constrains('price_include_taxes')
    def _constrains_pricelist_price_include(self):
        map_price_type = self.env['product.price.type']._get_tax_price_type()
        for rec in self:
            versions = self.env['product.pricelist.version'].search(
                [('pricelist_id', '=', rec.id)])
            items = self.env['product.pricelist.item'].search(
                [('price_version_id', 'in', versions._ids),
                 ('base', '>', '0'),  # TODO check other case
                 ('base', 'in', map_price_type[not rec.price_include_taxes])])
            if items:
                raise UserError(_(
                    "There are price rules like %s which have base field\n"
                    "not compatible with Tax defined on Pricelist" % items[0]))


class ProductPriceType(models.Model):
    _inherit = 'product.price.type'

    @api.model
    def _get_tax_price_type(self):
        map_price_type = defaultdict(list)
        for x in self.search([]):
            map_price_type[x.price_include_taxes].append(x.id)
        return map_price_type


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.multi
    @api.constrains('base')
    def _constrains_price_item_price_include(self):
        map_price_type = self.env['product.price.type']._get_tax_price_type()
        for rec in self:
            if rec.base >= 1:  # TODO check other case
                price_include_taxes = (
                    rec.price_version_id.pricelist_id.price_include_taxes)
                if rec.base not in map_price_type[price_include_taxes]:
                    price_type_name = self.env['product.price.type'].browse(
                        rec.base).name
                    raise UserError(
                        u"La règle de prix a le champ 'Base' "
                        u"dont le paramétrage de taxe ne correspond pas\n"
                        u"à celui de la liste de prix.\n"
                        u"Nom type prix : %s\n"
                        u"Champ TTC de la liste de prix : %s" % (
                            price_type_name, price_include_taxes))
