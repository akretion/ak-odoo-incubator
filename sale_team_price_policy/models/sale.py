# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.exceptions import Warning as UserError


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'price.policy.mixin']
    _name = 'sale.order'

    @api.constrains('state', 'section_id', 'partner_id', 'pricelist_id')
    def _check_pricelist_id(self):
        """
        Check if price policy of sale team are fulfilled.
        """
        for sale in self:
            if sale.state not in ('draft', 'cancel'):
                sale._check_price_policy()

    # For abilis price must be recalculted by wizard sale.order.recompute
    # (in custom)
    # @api.multi
    # def recalculate_prices(self):
    #     res = super(SaleOrder, self).recalculate_prices()
    #     self.write({'do_recalculate_price': False})
    #     return res

    @api.multi
    def action_button_confirm(self):
        if self.filtered('do_recalculate_price'):
            raise UserError(
                u"La liste de prix a été changée, "
                u"les prix doivent être recalculés."
                u"Pour recalculer les prix allez sur autre option puis"
                u"\"Mettre à jours les prix\"")
        return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def onchange_pricelist_id_new(self, pricelist_id, order_lines,
                                  section_id, context=None):
        res = super(SaleOrder, self).onchange_pricelist_id(
            pricelist_id, order_lines)
        if type(res) is dict and 'value' in res:
            for field, value in res.get('value').items():
                if hasattr(self, field):
                    setattr(self, field, value)
        if section_id:
            if isinstance(section_id, int):
                section_id = self.env['crm.case.section'].browse(section_id)
            pricelist_id_before = self.pricelist_id
            final = self._synchro_policy_fields(
                section=section_id, partner=self.partner_id)
            for key in final:
                if hasattr(self, key):
                    setattr(self, key, final[key])
            if self.pricelist_id.id != pricelist_id_before:
                if self.order_line:
                    self.do_recalculate_price = True
                # res['value']['pricelist_id'] = self.pricelist_id.id
                # import pdb; pdb.set_trace()
                # res['warning']['message'] = PRICE_POLICY_MESSAGE + \
                #     res['warning']['message']
        return res


PRICE_POLICY_MESSAGE = """
Pricelist is set by pricing policy on sales team.
It can't be updated for this sale team.

"""
