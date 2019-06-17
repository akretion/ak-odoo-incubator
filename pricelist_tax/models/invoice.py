# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange("product_id", "quantity", "uom_id")
    def _onchange_product_id_account_invoice_pricelist(self):
        self._add_pricelist_in_context()
        return super(
            AccountInvoiceLine, self
        )._onchange_product_id_account_invoice_pricelist()

    def _add_pricelist_in_context(self):
        # Sadly you can not use with_context in onchange
        # If you use it, all change are apply in the new env
        # and so at the end of the onchange the original env didn't change
        # and no onchange have been applyed
        ctx = self.env.context.copy()
        ctx["pricelist_id"] = self.invoice_id.pricelist_id.id
        self.env.context = ctx
