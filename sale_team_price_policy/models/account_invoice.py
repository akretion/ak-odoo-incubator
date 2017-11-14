# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Chafique DELLI <chafique.delli@akretion.com>
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
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
                _("Pricelist changed: Prices must be recomputed."))
        return super(AccountInvoice, self).invoice_validate()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        line = super(AccountInvoiceLine, self).create(vals)
        if self.env.context.get('install_mode') and line.invoice_id:
            inv = line.invoice_id
            res = line.product_id_change(
                line.product_id.id, line.uos_id.id, qty=line.quantity,
                name=line.name, type=inv.type,
                partner_id=line.partner_id.id,
                fposition_id=inv.fiscal_position, price_unit=line.price_unit,
                currency_id=inv.currency_id.id, company_id=inv.company_id.id)
            vals.update(res['value'])
            line.write(vals)
            inv.button_update_prices_from_pricelist()
        return line
