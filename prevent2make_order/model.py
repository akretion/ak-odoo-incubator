# coding: utf-8
# © 2015 Akretion Mourad EL HADJ MIMOUNE, David BEAL, Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from openerp.exceptions import Warning as UserError


# TODO use _register_hook() instead of this hack to code an independant module


class ForbiddenModel(models.AbstractModel):
    _name = 'forbidden.model'
    _description = u'Model qui verrouille ses enfants'

    @api.model
    def create(self, vals):
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        if url[-19:] == '/asler.akretion.com':
            raise UserError(u"Création interdite de '%s' sur la base "
                            u"de production\nUtilsez la base de "
                            u"preproduction à la place." % self._description)
        return super(ForbiddenModel, self).create(vals)


class AccountInvoice(models.Model):
    _inherit = ['account.invoice', 'forbidden.model']
    _name = 'account.invoice'


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'forbidden.model']
    _name = 'sale.order'


class PurchaseOrder(models.Model):
    _inherit = ['purchase.order', 'forbidden.model']
    _name = 'purchase.order'


class StockPicking(models.Model):
    _inherit = ['stock.picking', 'forbidden.model']
    _name = 'stock.picking'
