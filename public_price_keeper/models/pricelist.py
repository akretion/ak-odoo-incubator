# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)

SEQUENCE = 999999
PRICE_ITEM_NAME = "Default price rule based on public price"


class ProductPricelistVersion(models.Model):
    _inherit = 'product.pricelist.version'

    @api.model
    def create(self, vals):
        res = super(ProductPricelistVersion, self).create(vals)
        pricelist = self.env['product.pricelist'].browse(
            vals.get('pricelist_id'))
        if pricelist.type == 'sale':
            item_vals = {
                'default_item': True,
                'base': 1,
                'name': PRICE_ITEM_NAME,
                'sequence': SEQUENCE,
                'price_version_id': res.id,
            }
            self.env['product.pricelist.item'].create(item_vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            item = self.env['product.pricelist.item'].search(
                [('default_item', '=', True)])
            if item:
                # we must delete default item
                item.with_context(unlink_defaut_item=True).unlink()
        return super(ProductPricelistVersion, self).unlink()


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    default_item = fields.Boolean(
        string='Default Item',
        help="Default price item is based on public price and is applied "
             "when no other item is found.")

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.default_item and not self._context.get(
                    'unlink_defaut_item'):
                raise UserError(
                    _("You must keep a pricelist item named '%s' "
                      "inside each pricelist version" % PRICE_ITEM_NAME))
        return super(ProductPricelistItem, self).unlink()

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.default_item:
                # Some modules update price items, we bypass their behavior
                vals = {}
                _logger.info("Price item '%s' update is bypassed by "
                             "public_price_keeper module", PRICE_ITEM_NAME)
        res = super(ProductPricelistItem, self).write(vals)
        return res
