# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, models
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
        """ Override Odoo method to:
            - use raw price from pricelist (if price exclude)
              instead of recomputed price
            - some checks/raises on unmanaged cases
        """
        pricelist = self.env["product.pricelist"].browse(
            self.env.context.get("pricelist_id")
        )
        if pricelist and not pricelist.price_include_taxes:
            self._check_product_taxes(prod_taxes)
            if all([not x.price_include for x in line_taxes]):
                # The taxes on the line are all taxes excluded
                # we can directly return the original price of
                # the product directly because it's tax excluded too
                # Returning it directly avoid rounding issue by converting
                # it to tax included and then back to tax excluded
                return price
            else:
                # Some taxes on the line included taxes
                # We need to compute the price tax included of the product
                # So Odoo native code can compute correcly the price
                taxes = self.browse(False)
                for tax in prod_taxes:
                    taxes |= tax._map_included_to_excluded_taxes()
                price = taxes.compute_all(price)["total_included"]
        return super(AccountTax, self)._fix_tax_included_price(
            price, prod_taxes, line_taxes
        )

    def _map_domain(self):
        return [
            ("type_tax_use", "=", self.type_tax_use),
            ("tax_group_id", "=", self.tax_group_id.id),
            ("company_id", "=", self.company_id.id),
            ("amount", "=", self.amount),
            ("amount_type", "=", self.amount_type),
            ("price_include", "=", False),
        ]

    def _map_included_to_excluded_taxes(self):
        self.ensure_one()
        tax_exc = self.search(self._map_domain())
        if len(tax_exc) == 1:
            return tax_exc
        else:
            raise UserError(
                _(
                    "Fail to find the tax excluded equivalent of %s. "
                    "%s taxes found"
                )
                % self.name,
                len(tax_exc),
            )

    def _check_product_taxes(self, prod_taxes):
        prod_taxes_exclude = [x for x in prod_taxes if not x.price_include]
        if prod_taxes_exclude:
            raise UserError(
                _(
                    "Since you have installed the product 'pricelist_tax'"
                    "The tax on the product must be tax included"
                    "This taxt '%s' is price exclude. "
                    "Please fix it."
                )
                % prod_taxes_exclude[0].name
            )
