# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .models.pricelist import (
    SEQUENCE,
    PRICE_ITEM_NAME)


def post_init_hook(cr, registry):
    """ Add a pricelist.item for each pricelist.version
    """
    price_version_ids = registry['product.pricelist.version'].search(cr, 1, [
        ('pricelist_id.type', '=', 'sale')])
    vals = {
        'default_item': True,
        'base': 1,
        'name': PRICE_ITEM_NAME,
        'sequence': SEQUENCE,
    }
    # we remove old if exists to avoid duplicates
    item_ids = registry['product.pricelist.item'].search(cr, 1, [
        ('name', '=', PRICE_ITEM_NAME)])
    registry['product.pricelist.item'].unlink(cr, 1, item_ids)
    # we create items
    for version in registry['product.pricelist.version'].browse(
            cr, 1, price_version_ids):
        vals['price_version_id'] = version.id
        registry['product.pricelist.item'].create(cr, 1, vals)
