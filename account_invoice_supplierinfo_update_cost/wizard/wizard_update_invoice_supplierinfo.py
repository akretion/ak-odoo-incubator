# -*- coding: utf-8 -*-
# © 2018 Pierrick Brun @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
    _inherit = "wizard.update.invoice.supplierinfo"

    update_cost = fields.Boolean(default=True)

    @api.multi
    def update_supplierinfo(self):
        super(WizardUpdateInvoiceSupplierinfo, self).update_supplierinfo()
        for record in self:
            if record.update_cost:
                for line in record.line_ids:
                    if line.product_id:
                        line.product_id.standard_price = line.new_price
