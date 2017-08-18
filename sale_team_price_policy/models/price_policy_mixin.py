# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError


class PricePolicyMixin(models.AbstractModel):
    _name = 'price.policy.mixin'

    do_recalculate_price = fields.Boolean(
        help=u"Cette case est coché automatiquement après "
             u"le changement de la liste de prix.")

    @api.multi
    @api.onchange('section_id', 'partner_id', 'pricelist_id')
    def _pp_onchange_section_id(self):
        for record in self:
            if record.section_id:
                pricelist_id_before = record.pricelist_id
                if record.section_id.price_policy == 'contract_pricelist':
                    record.pricelist_id = record.section_id.pricelist_id

                if record.section_id.price_policy ==\
                        'partner_pricelist_if_not_default':
                    if not record.partner_id.property_product_pricelist.\
                            is_default_pricelist:
                        record.pricelist_id =\
                            record.partner_id.property_product_pricelist
                    else:
                        record.pricelist_id = record.section_id.pricelist_id
                elif record.section_id.price_policy == 'partner_pricelist':
                    record.pricelist_id =\
                        record.partner_id.property_product_pricelist
                if record.pricelist_id != pricelist_id_before:
                    if getattr(record, 'order_line', None) or\
                            getattr(record, 'invoice_line', None):
                        record.do_recalculate_price = True


    # @api.multi
    # # @api.onchange('pricelist_id')
    # def onchange_pricelist_id(self, pricelist_id):
    #     import pdb; pdb.set_trace()
    #     return super(SaleOrder, self).onchange_pricelist_id(pricelist_id)
    #     for record in self:
    #         import pdb; pdb.set_trace()
    #         if record.pricelist_id and record.state == 'draft':
    #             for line in record.record_line:
    #                 if not line.record_line_ids:
    #                     line.update_from_pricelist()

    # @api.multi
    # def onchange(self, values, field_name, field_onchange):
    #     # To avoid hard inheriting on partner_id we always play the section_id
    #     print "###############field_name############"
    #     print field_name
    #     if isinstance(field_name, list) and 'section_id' in field_name:
    #         field_name.remove('section_id')
    #         field_name.append('section_id')
    #     # If we call an onchange on the partner_id we also call the onchange
    #     # on the section_id for the compatibility
    #     if field_name == 'partner_id':
    #         field_name = ['partner_id', 'section_id']
    #     if field_name == 'pricelist_id':
    #         field_name = ['pricelist_id', 'section_id']
    #     return super(SaleOrder, self).onchange(
    #         values, field_name, field_onchange)

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
                HELP_PRICELIST + u" prix du marché " + HELP_POLICY)

        if self.section_id.price_policy ==\
                'partner_pricelist_if_not_default':
            if not self.partner_id.property_product_pricelist.\
                    is_default_pricelist and self.pricelist_id !=\
                    self.partner_id.property_product_pricelist:
                raise UserError(
                    HELP_PRICELIST + u" prix du client " + HELP_POLICY)
            elif self.pricelist_id != self.section_id.pricelist_id:
                raise UserError(
                    HELP_PRICELIST + u" prix du marché " + HELP_PRICELIST)
        if self.section_id.price_policy ==\
                'partner_pricelist_if_not_default' and \
                self.pricelist_id != \
                self.partner_id.property_product_pricelist:
            raise UserError(
                HELP_PRICELIST + u" prix du client " + HELP_POLICY)


HELP_PRICELIST = u"La liste de prix de vente, doit correspondre à la liste de"

HELP_POLICY = u"""(voir la politique tarifaire sur le marché:
                   équipe commerciale)"""
