# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import TransactionCase


class TestPriceKeeper(TransactionCase):

    def test_check_public_price_keeper_number(self):
        default_items = self.env['product.pricelist.item'].search_count(
            [('default_item', '=', True)])
        sale_price_versions = self.env['product.pricelist.version'] \
            .search_count([('pricelist_id.type', '=', 'sale')])
        self.assertEqual(
            default_items, sale_price_versions,
            "You must have as many sale pricelist versions "
            "as base_item pricelist")

    def test_check_public_price_keeper_validity(self):
        items = self.env['product.pricelist.item'].search(
            ['|',
             ('price_surcharge', '!=', 0),
             ('price_discount', '!=', 0),
             ('categ_id', '!=', False),
             ('product_id', '!=', False),
             ('product_tmpl_id', '!=', False),
             ('default_item', '=', True),
             ], order='price_version_id')
        self.assertEqual(
            items, self.env['product.pricelist.item'],
            "These pricelist items\n %s \n are wrong !"
            % ["'%(item)s' id %(id)s, version %(version)s\n" % {
                'item': x.name, 'id': x.id,
                'version': x.price_version_id.name or ''}
               for x in items])
