# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_taxes_values(self):
        map_tax = self.env['account.tax']._map_exclude_tax()
        if not self.pricelist_id.price_include_taxes:
            for line in self.invoice_line_ids:
                print '\n\nJe passe dans plist_tax/get_taxes_values'
                _logger.debug("Tax before %s",
                              [x.name for x in line.invoice_line_tax_ids])
                line.invoice_line_tax_ids = self.env[
                    'account.tax']._get_substitute_taxes(
                    line, line.invoice_line_tax_ids, map_tax)
                _logger.debug("Tax after %s",
                              [x.name for x in line.invoice_line_tax_ids])
        return super(AccountInvoice, self).get_taxes_values()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        # super(AccountInvoiceLine, self)._set_taxes()
        if not self.invoice_id.pricelist_id.price_include_taxes:
            # Just a big copy/paste from odoo except ## below
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                taxes = self.product_id.taxes_id or self.account_id.tax_ids
            else:
                taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids

            # Keep only taxes of the company
            company_id = self.company_id or self.env.user.company_id
            taxes = taxes.filtered(lambda r: r.company_id == company_id)

            self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id, self.invoice_id.partner_id)
            ## Here to sustitute tax
            map_tax = self.env['account.tax']._map_exclude_tax()
            self.invoice_line_tax_ids = fp_taxes = self.env[
                'account.tax']._get_substitute_taxes(self, fp_taxes, map_tax)

            ## Here add context to put pricelist
            import pdb; pdb.set_trace()
            fix_price = self.env['account.tax'].with_context(pricelist=self.invoice_id.pricelist_id.id)._fix_tax_included_price

            if self.invoice_id.type in ('in_invoice', 'in_refund'):
                prec = self.env['decimal.precision'].precision_get('Product Price')
                if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=prec) == 0:
                    self.price_unit = fix_price(self.product_id.standard_price, taxes, fp_taxes)
                    self._set_currency()
            else:
                self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)
                self._set_currency()
