# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)

SEQUENCE = 999999
PRICE_ITEM_NAME = "Default price rule based on public price"


def get_pricelist_item_vals():
    return {
        'base_item': True,
        'base': 1,
        'price_discount': 0,
        'price_surcharge': 0,
        'name': PRICE_ITEM_NAME,
        'sequence': SEQUENCE,
    }


class ProductPricelistVersion(models.Model):
    _inherit = 'product.pricelist.version'

    @api.model
    def create(self, vals):
        res = super(ProductPricelistVersion, self).create(vals)
        pricelist = self.env['product.pricelist'].browse(
            vals.get('pricelist_id'))
        if pricelist.type == 'sale':
            item_vals = get_pricelist_item_vals()
            item_vals['price_version_id'] = res.id,
            self.env['product.pricelist.item'].create(item_vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            item = self.env['product.pricelist.item'].search(
                [('base_item', '=', True)])
            if item:
                # we must delete base item
                item.with_context(unlink_base_item=True).unlink()
        return super(ProductPricelistVersion, self).unlink()


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    base_item = fields.Boolean(
        string='Default Item',
        help="Default price item is based on public price and is applied "
             "when no other item is found.")

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.base_item and not self._context.get('unlink_base_item'):
                raise UserError(
                    _("You must keep a pricelist item named '%s' \n"
                      "inside each pricelist version" % PRICE_ITEM_NAME))
        return super(ProductPricelistItem, self).unlink()

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.base_item:
                # Some modules update price items, we bypass their behavior
                vals = {}
                _logger.info("Price item '%s' update is bypassed by "
                             "public_price_keeper module", PRICE_ITEM_NAME)
        return super(ProductPricelistItem, self).write(vals)
