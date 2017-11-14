# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class PricePolicyMixin(models.AbstractModel):
    _name = 'price.policy.mixin'

    do_recalculate_price = fields.Boolean(
        help="Checked after the pricelist update for recomputing later.")

    @api.multi
    @api.onchange('section_id', 'partner_id', 'pricelist_id')
    def _pp_onchange_section_id(self):
        for record in self:
            if record.section_id:
                pricelist_id_before = record.pricelist_id
                final = record._synchro_policy_fields(
                    section=record.section_id, partner=record.partner_id)
                for key in final:
                    if hasattr(record, key):
                        setattr(record, key, final[key])
                if record.pricelist_id != pricelist_id_before:
                    if getattr(record, 'order_line', None) or \
                            getattr(record, 'invoice_line', None):
                        record.do_recalculate_price = True

    @api.model
    def _synchro_policy_fields(self, section=None, partner=None):
        """ Make the same behavior between onchange and crud methods """
        final = {}
        if section.price_policy == 'contract_pricelist':
            final['pricelist_id'] = section.pricelist_id.id
        elif section.price_policy == \
                'partner_pricelist_if_exists':
            if partner.property_product_pricelist:
                final['pricelist_id'] = partner.property_product_pricelist.id
            else:
                final['pricelist_id'] = section.pricelist_id.id
        elif section.price_policy == 'partner_pricelist':
            final['pricelist_id'] = partner.property_product_pricelist.id
        return final

    @api.model
    def create(self, vals):
        if vals.get('section_id'):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            section = self.env['crm.case.section'].browse(vals['section_id'])
            vals.update(
                self._synchro_policy_fields(section=section, partner=partner))
        return super(PricePolicyMixin, self).create(vals)

    @api.model
    def _check_price_policy(self):
        """
        Check if price policy of record team are fulfilled.
        We check only for customer invoice (not supplier invoice nor refunds)
        """
        self.ensure_one()
        if self.section_id.price_policy == 'contract_pricelist' and \
                self.pricelist_id != self.section_id.pricelist_id:
            raise UserError(
                HELP_PRICELIST + _(" market price ") + HELP_POLICY)
        if self.section_id.price_policy == 'partner_pricelist_if_exists':
            if self.partner_id.property_product_pricelist:
                if self.partner_id.property_product_pricelist \
                        != self.pricelist_id:
                    raise UserError(
                        HELP_PRICELIST + _(" customer price ") + HELP_POLICY)
            elif self.section_id.pricelist_id != self.pricelist_id:
                raise UserError(
                    HELP_PRICELIST + _(" market price ") + HELP_PRICELIST)
        if self.section_id.price_policy == 'partner_pricelist' and \
                self.pricelist_id != \
                self.partner_id.property_product_pricelist:
            raise UserError(
                HELP_PRICELIST + _(" customer price ") + HELP_POLICY)


HELP_PRICELIST = u"Sale pricelist must match to "

HELP_POLICY = u""" pricelist (see Sales team - Pricing tab)"""
