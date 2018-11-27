# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TaxCase(TransactionCase):

    def setUp(self):
        super(TaxCase, self).setUp()
        self.ht_plist = self.env.ref('pricelist_tax.ht_pricelist')
        self.ttc_plist = self.env.ref('pricelist_tax.ttc_pricelist')
        self.fp_intra = self.env.ref(
            'l10n_fr.1_fiscal_position_template_intraeub2b').id
        self.fp_exp = self.env.ref(
            'l10n_fr.1_fiscal_position_template_import_export').id
        self.solo = self.env['sale.order.line']

    def _create_object(self, model, pricelist):
        # Create a sale order or invoice
        return self.env[model].create({
            'partner_id': self.env.ref('base.res_partner_10').id,
            'pricelist_id': pricelist.id,
        })

    def _prepare_sale_vals(self):
        return {
            'product_uom_qty': 1,
            'product_id': self.env.ref('pricelist_tax.ak_product').id,
        }

    def _prepare_invoice_vals(self):
        return {
            'quantity': 1,
            'product_id': self.env.ref('pricelist_tax.ak_product').id,
        }

    def test_product_price(self):
        # HT
        rule = self.ht_plist.get_product_price_rule(
            self.env.ref('pricelist_tax.ak_product'), 1,
            self.env.ref('base.res_partner_10'))
        self.assertEqual(rule[0], 7.0, "Product price HT is not OK")
        # TTC
        rule = self.ttc_plist.get_product_price_rule(
            self.env.ref('pricelist_tax.ak_product'), 1,
            self.env.ref('base.res_partner_10'))
        self.assertEqual(rule[0], 8.0, "Product price TTC is not OK")

    def test_sale_tax_ht(self):
        record = self._create_object('sale.order', self.ht_plist)
        vals = self._prepare_sale_vals()
        vals['order_id'] = record.id
        vals = self.env['sale.order.line'].play_onchanges(vals, vals.keys())
        record.write({'order_line': [(0, 0, vals)]})
        expected_amount = 7.0  # Same value in sale
        self._sale_common_checks('sale ht test:', record, expected_amount)

    def test_sale_tax_ttc(self):
        record = self._create_object('sale.order', self.ttc_plist)
        vals = self._prepare_sale_vals()
        vals['order_id'] = record.id
        vals = self.env['sale.order.line'].play_onchanges(vals, vals.keys())
        record.write({'order_line': [(0, 0, vals)]})
        expected_amount = 6.67
        self._sale_common_checks('sale ttc test:', record, expected_amount)

    def _sale_common_checks(self, test, sale, amount):
        used_tax = sale.order_line[0].tax_id
        self.assertEqual(
            sale.order_line[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
        sale.write({'fiscal_position_id': self.fp_intra})
        self.assertEqual(
            sale.order_line[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
        sale.write({'fiscal_position_id': False})
        self.assertEqual(sale.order_line[0].tax_id, used_tax,
                         "%s Tax on sale without fisc. pos. is not the same "
                         "after tried/reverted another fisc. pos. " % test)
        self.assertEqual(
            sale.order_line[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)

    def test_invoice_tax_ht(self):
        # Same test than in sale gt
        record = self._create_object('account.invoice', self.ht_plist)
        vals = self._prepare_invoice_vals()
        vals['invoice_id'] = record.id
        print 'before vals', vals
        vals = self.env['account.invoice.line'].play_onchanges(
            vals, vals.keys())
        print 'after vals', vals
        record.write({'invoice_line_ids': [(0, 0, vals)]})
        print 'Taxe de la ligne', [x.name for x in record.invoice_line_ids[0].invoice_line_tax_ids]
        import pdb; pdb.set_trace()
        expected_amount = 7.0
        self._invoice_common_checks(
            'invoice ht test:', record, expected_amount)

    # def test_invoice_tax_ttc(self):
    #     # Same test than in sale ttc
    #     record = self._create_object('account.invoice', self.ht_plist)
    #     vals = self._prepare_invoice_vals()
    #     vals['invoice_id'] = record.id
    #     vals = self.env['account.invoice.line'].play_onchanges(
    #         vals, vals.keys())
    #     record.write({'invoice_line_ids': [(0, 0, vals)]})
    #     expected_amount = 6.67
    #     self._invoice_common_checks(
    #         'invoice ttc test:', record, expected_amount)

    def _invoice_common_checks(self, test, inv, amount):
        used_tax = inv.invoice_line_ids[0].invoice_line_tax_ids
        print '\n\n\nused_tax', used_tax.name
        self.assertEqual(
            inv.invoice_line_ids[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
        inv.write({'fiscal_position_id': self.fp_intra})
        self.assertEqual(
            inv.invoice_line_ids[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
        inv.write({'fiscal_position_id': False})
        self.assertEqual(
            inv.invoice_line_ids[0].invoice_line_tax_ids, used_tax,
            "%s Tax on invoice without fisc. pos. is not the same "
            "after tried/reverted another fisc. pos. " % test)
        self.assertEqual(
            inv.invoice_line_ids[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
