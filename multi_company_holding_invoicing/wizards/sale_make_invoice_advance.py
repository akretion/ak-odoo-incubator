# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models
from odoo.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sales = self.env["sale.order"].search(
            [
                ("id", "in", self._context["active_ids"]),
                ("holding_company_id", "!=", False),
            ]
        )
        if sales:
            raise UserError(_("This sale order must be invoiced from holding"))
        return super(SaleAdvancePaymentInv, self).create_invoices()
