# coding: utf-8
#  @author Raphael Reverdy @ Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _roulier_get_account(self, package):
        """Returns an 'account'.

        We return an account based on the delivery method's technical name"""
        self.ensure_one()
        keychain = self.env['keychain.account']
        if self.env.user.has_group('stock.group_stock_user'):
            retrieve = keychain.suspend_security().retrieve
        else:
            retrieve = keychain.retrieve

        shop = self.sale_id.shop_id or self.env["sale.shop"].search([], order="id asc", limit=1)
        method = self.carrier_id

        sale_shop_methods = self.env['sale.shop.method'].search(
            [
                ['shop', '=', shop.id],
                ['delivery_methods', 'in', (method.id)],
            ])

        if len(sale_shop_methods) < 1:
            _logger.debug(
                'At least 1 sale_shop_method should be found %s %s' %
                (shop, method.id)
            )
            raise UserError("Shop / Account / Delivery not well configured \
                             for picking %s" % self.name)

        accounts = retrieve(
            [
                ['namespace', '=', 'roulier_%s' % self.carrier_type],
                ['shop_methods', 'in', sale_shop_methods.ids]
            ])
        if len(accounts) != 1:
            _logger.debug('Searching an account for %s' % shop)
            raise UserError("No account or multiple accounts found based on \
                             the shop, for picking %s" % self.name)

        return accounts[0]

    def _roulier_get_sender(self, package):
        shop = self.sale_id.shop_id
        return shop.shipping_sender_id or shop.partner_id
