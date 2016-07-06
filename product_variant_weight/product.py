# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp


def get_weight_ratio(self):
    ResCompany = self.env['res.company']
    company_id = ResCompany._company_default_get(object=self._name)
    return ResCompany.browse(company_id).weight_ratio or 0


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight = fields.Float(compute='_raise_me')
    weight_net = fields.Float(compute='_raise_me')
    weight_tmpl = fields.Float(
        string="Template Gross Weight",
        digits_compute=dp.get_precision('Stock Weight'),
        help="The gross weight in Kg of the product template.")
    weight_net_tmpl = fields.Float(
        string='Template Net Weight',
        digits_compute=dp.get_precision('Stock Weight'),
        help="The net weight in Kg of the product template.")

    @api.onchange('weight_net_tmpl')
    def onchange_net_weight(self):
        # TODO make it works in multicompany
        if not self.weight_tmpl:
            self.weight_tmpl = self.weight_net_tmpl * get_weight_ratio(self)

    @api.model
    def _raise_me(self):
        raise UserError(_(
            u"Weight fields must come from product.product model."
            u"This constraint has been added by "
            u"'Product Variant Weight' module."
            u"Please call you support team."))


class ProductProduct(models.Model):
    _inherit = 'product.product'

    weight = fields.Float(
        string="Gross Weight", compute='_get_weight', store=True,
        digits_compute=dp.get_precision('Stock Weight'),
        help="The gross weight in Kg.")
    weight_net = fields.Float(
        string='Net Weight', compute='_get_weight', store=True,
        digits_compute=dp.get_precision('Stock Weight'),
        help="The net weight in Kg.")
    weight_variant = fields.Float(
        string='Variant Weight',
        digits_compute=dp.get_precision('Stock Weight'),
        help="The addtionnal part of weight in Kg on variant.")
    weight_net_variant = fields.Float(
        string='Variant Net Weight',
        digits_compute=dp.get_precision('Stock Weight'),
        help="The addtionnal part of net weight in Kg on variant.")

    @api.onchange('weight_net_variant')
    def onchange_net_weight(self):
        # TODO make it works in multicompany
        if not self.weight_variant:
            self.weight_variant = (
                self.weight_net_variant * get_weight_ratio(self))

    @api.multi
    @api.depends('weight_variant',
                 'weight_net_variant',
                 'product_tmpl_id.weight_tmpl',
                 'product_tmpl_id.weight_net_tmpl')
    def _get_weight(self):
        for prod in self:
            prod.weight = prod.weight_tmpl + prod.weight_variant
            prod.weight_net = prod.weight_net_tmpl + prod.weight_net_variant
