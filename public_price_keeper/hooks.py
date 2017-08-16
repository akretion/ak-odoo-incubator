# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .models.pricelist import (
    get_pricelist_item_vals,
    PRICE_ITEM_NAME
)


def post_init_hook(cr, registry):
    """ Add a pricelist.item for each pricelist.version
    """
    domain = registry['product.pricelist.version']\
        ._get_keep_public_price_domain(cr, 1)
    price_version_ids = registry['product.pricelist.version'].search(
        cr, 1, domain)
    vals = get_pricelist_item_vals()
    # we remove old if exists to avoid duplicates
    item_ids = registry['product.pricelist.item'].search(cr, 1, [
        ('name', '=', PRICE_ITEM_NAME)])
    registry['product.pricelist.item'].unlink(cr, 1, item_ids)
    # we create items
    for version in registry['product.pricelist.version'].browse(
            cr, 1, price_version_ids):
        vals['price_version_id'] = version.id
        registry['product.pricelist.item'].create(cr, 1, vals)
