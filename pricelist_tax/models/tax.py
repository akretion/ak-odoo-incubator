# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, api, _
from odoo.exceptions import UserError

from cStringIO import StringIO
from lxml import etree

import codecs

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _get_linked_record(self):
        # {'model': 'sale.order.line', 'xml_id': 'public1',
        # 'xml_file': u'/odoo/local-src/recette_company/demo/sale.xml',
        # 'module': u'recette_company'}
        imd = self.env.context['install_mode_data']
        found = False
        with codecs.open(imd['xml_file'], mode='r', encoding='utf-8') as f:
            content = f.read().replace('<?xml version="1.0"?>', '')
            doc = etree.parse(StringIO(content))
            nodes = False
            for elm in doc.getroot().iterchildren():
                if not (elm.attrib['model'] == imd['model'] and
                        elm.attrib['id'] == imd['xml_id']):
                    continue
                nodes = elm.getchildren()
                break
            for elm in nodes:
                if not elm.attrib['name'] == 'order_id':
                    continue
                found = elm.attrib.get('ref')
                break
        if found:
            return self.env.ref('%s.%s' % (imd['module'], found))
        return False

    @api.model
    def _filter_product_taxes(self, prod_taxes):
        """ Use the most appropriate company to minimize taxes:
            - SuperAdmin read all taxes whatever the companies in most cases
            - Context may contains informations:
                * 'company_id' key
                * 'install_mode_data' key lead to all needed informations
        """
        company_id = False
        if 'install_mode_data' in self.env.context:
            company_id = self._get_linked_record().company_id.id
            print 'Cooooooompany', company_id
        concerned_company_id = company_id or self.env.context.get(
            'company_id') or self.env.user.company_id.id
        return prod_taxes.filtered(
            lambda r: r.company_id.id == concerned_company_id)

    @api.model
    def _guess_company(self):
        """ Use the most appropriate company to minimize taxes:
            - SuperAdmin read all taxes whatever the companies in most cases
            - Context may contains informations:
                * 'company_id' key
                * 'install_mode_data' key lead to all needed informations
        """
        company_id = False
        if 'install_mode_data' in self.env.context:
            company_id = self._get_linked_record().company_id.id
            print 'CooOOOOooompany', company_id
        return company_id or self.env.context.get(
            'company_id') or self.env.user.company_id.id

    @api.model
    def _fix_tax_included_price_company(
            self, price, prod_taxes, line_taxes, company_id):
        if not company_id:
            company_id = self._guess_company()
        return super(AccountTax, self)._fix_tax_included_price_company(
            price, prod_taxes, line_taxes, company_id)

    # @api.model
    # def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
    #     """ Override Odoo method to:
    #         - use raw price from pricelist (if price exclude)
    #           instead of recomputed price
    #         - some checks/raises on unmanaged cases
    #     """
    #     # print prod_taxes
    #     prod_taxes = self._filter_product_taxes(prod_taxes)
    #     line_taxes = self._filter_product_taxes(line_taxes)
    #     # print prod_taxes, line_taxes
    #     # import pdb; pdb.set_trace()
    #     self._check_unsupported_case(prod_taxes=prod_taxes)
    #     original = super(AccountTax, self)._fix_tax_included_price(
    #         price, prod_taxes, line_taxes)
    #     pricelist_id = self.env.context.get('pricelist')
    #     computed_price = False
    #     # Check if pricelist contains adhoc price
    #     if pricelist_id:
    #         pricelist = self.env['product.pricelist'].browse(pricelist_id)
    #         if not pricelist.price_include_taxes:
    #             computed_price = True
    #             self._check_unsupported_case(
    #                 line_taxes=line_taxes, pricelist=pricelist)
    #     if computed_price:
    #         return price
    #     return original

    def _check_unsupported_case(
            self, prod_taxes=None, line_taxes=None, pricelist=None):
        if prod_taxes:
            prod_taxes_exclude = [x for x in prod_taxes if not x.price_include]
            if prod_taxes_exclude:
                message = _("Tax product '%s' is price exclude. "
                            "You must switch to include ones."
                            % prod_taxes_exclude[0].name)
                _logger.warning(message)
                raise UserError(message)
        if line_taxes:
            line_taxes_include = [x for x in line_taxes if x.price_include]
            if line_taxes_include:
                tax_mess = ' ; '.join(
                    [x.name for x in line_taxes_include])
                print '\n\n', prod_taxes, line_taxes, tax_mess
                message = _("Tax with include price with pricelist b2b '%s' "
                            "is not supported.\nThis tax '%s' is inside one "
                            "of your sale lines doesn't match with "
                            "this pricelist" % (pricelist.name, tax_mess))
                _logger.warning(message.replace('\n', ' '))
                raise UserError(message)
