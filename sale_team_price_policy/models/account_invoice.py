# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Chafique DELLI <chafique.delli@akretion.com>
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = ['account.invoice', 'price.policy.mixin']
    _name = 'account.invoice'

    pricelist_id = fields.Many2one(required=True)

    @api.constrains('state', 'section_id', 'partner_id', 'pricelist_id')
    def _check_pricelist_id(self):
        """
        Check if price policy of invoice team are fulfilled.
        We check only for customer invoice (not supplier invoice nor refunds)
        """
        for inv in self:
            if inv.state not in ('draft', 'cancel') and\
                    inv.type == 'out_invoice':
                inv._check_price_policy()

    @api.multi
    def button_update_prices_from_pricelist(self):
        res = super(AccountInvoice, self).\
            button_update_prices_from_pricelist()
        self.write({'do_recalculate_price': False})
        return res

    @api.multi
    def invoice_validate(self):
        if self.filtered('do_recalculate_price'):
            raise UserError(
                u"La liste de prix a été changé, "
                u"les prix doivent être recalculés,")
        return super(AccountInvoice, self).invoice_validate()
