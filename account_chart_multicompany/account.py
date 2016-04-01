# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2016 Akretion (http://www.akretion.com).
#   @author Chafique DELLI <chafique.delli@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_tmpl_id = fields.Many2one('account.tax.template',
                                  string='Tax Account Template')


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    tax_ids = fields.One2many('account.tax', 'tax_tmpl_id',
                              string='Tax Account List')

    @api.model
    def _generate_tax(self, tax_templates, tax_code_template_ref, company_id):
        tax_template_ref = super(AccountTaxTemplate, self)._generate_tax(
            tax_templates, tax_code_template_ref, company_id)
        for tax_tmpl_id, tax_id in tax_template_ref['tax_template_to_tax']\
                .iteritems():
            tax = self.env['account.tax'].browse(tax_id)
            tax.write({'tax_tmpl_id': tax_tmpl_id})
        return tax_template_ref

    @api.multi
    def force_generate_tax(self):
        for tax_account_template in self:
            chart_template = tax_account_template.chart_template_id
            tax_code_tmpl_obj = self.env['account.tax.code.template']
            for tax in chart_template.tax_template_ids[0].suspend_security()\
                    .tax_ids:
                tax_code_template_ref = tax_code_tmpl_obj\
                    .suspend_security()\
                    .generate_tax_code(
                        chart_template.tax_code_root_id.id, tax.company_id.id)
                self.suspend_security()._generate_tax(
                    tax_account_template, tax_code_template_ref,
                    tax.company_id.id)

    @api.model
    def create(self, vals):
        tax_account_template = super(AccountTaxTemplate, self).create(vals)
        if 'install_mode' not in self._context:
            tax_account_template.force_generate_tax()
        return tax_account_template

    @api.multi
    def write(self, vals):
        field_list = ['name', 'description', 'type', 'type_tax_use', 'amount']
        tax_vals = {}
        for field in field_list:
            if field in vals:
                tax_vals[field] = vals[field]
        if tax_vals and self.suspend_security().tax_ids:
            self.suspend_security().tax_ids.write(tax_vals)
        return super(AccountTaxTemplate, self).write(vals)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_tmpl_id = fields.Many2one('account.account.template',
                                      string='Account Template')
    @api.cr
    def _parent_store_compute(self, cr):
        if hasattr(cr, 'skip_parent_recompute') and cr.skip_parent_recompute:
            _logger.info("SKIP PARENT LEFT/RIGHT RECOMPUTATION FOR ACCOUNT")
            return True
        _logger.info("MASSIVE SQL PARENT LEFT/RIGHT RECOMPUTATION FOR ACCOUNT")
        cr.execute("""WITH RECURSIVE compute_parent(id, pleft, prigth) AS (
            SELECT id, 1::INT AS pleft, company_id * 10000::INT AS prigth
                FROM account_account
                WHERE parent_id IS NULL
                UNION ALL
                SELECT
                    c.id,
                    ct.pleft + (
                        (ct.prigth - ct.pleft) *
                            (1- row_number() OVER (
                                PARTITION BY c.parent_id
                                ORDER BY c.parent_id asc)::FLOAT
                            / sum(1) OVER (
                                PARTITION BY c.parent_id
                                ORDER BY c.parent_id desc)))::INT + 1 AS pleft,
                    ct.pleft + (
                        (ct.prigth - ct.pleft) *
                             (1-(row_number() OVER (
                                PARTITION BY c.parent_id
                                ORDER BY c.parent_id asc)-1)::FLOAT
                            / sum(1) OVER (
                                PARTITION BY c.parent_id
                                ORDER BY c.parent_id desc)))::INT -1 AS pright
                FROM account_account c
                JOIN compute_parent ct ON ct.id = c.parent_id
            ) UPDATE account_account
              SET parent_right=prigth, parent_left=pleft
              FROM compute_parent
              WHERE compute_parent.id = account_account.id""")
        return True


class AccountAccountTemplate(models.Model):
    _inherit = 'account.account.template'

    account_ids = fields.One2many('account.account', 'account_tmpl_id',
                                  string='Account List')

    @api.model
    def generate_account(self, chart_template_id, tax_template_ref,
                         acc_template_ref, code_digits, company_id):
        acc_template_ref = super(AccountAccountTemplate, self)\
            .generate_account(
                chart_template_id, tax_template_ref, acc_template_ref,
                code_digits, company_id)
        for account_tmpl_id, account_id in acc_template_ref.iteritems():
            account = self.env['account.account'].browse(account_id)
            account.write({'account_tmpl_id': account_tmpl_id})
        return acc_template_ref

    @api.model
    def create(self, vals):
        account_template = super(AccountAccountTemplate, self).create(vals)
        if 'install_mode' not in self._context:
            # HACK on cursor for avoiding multi parent recompute
            setattr(self._cr, 'skip_parent_recompute', True)
            acc_template_ref = {}
            parent_id = account_template.parent_id
            for account in parent_id.suspend_security().account_ids:
                acc_template_ref[parent_id.id] = account.id
                code_digits = len(account.code)
                tax_template_ref = {}
                for tax_template in account_template.tax_ids:
                    for tax in tax_template.tax_ids:
                        if tax.company_id.id == account.company_id.id:
                            tax_template_ref[tax_template.id] = tax.id
                chart_template_id = account_template.chart_template_id.id
                self.suspend_security().with_context(
                    force_id_for_search=account_template.id)\
                    .generate_account(
                        chart_template_id, tax_template_ref,
                        acc_template_ref, code_digits, account.company_id.id)
            setattr(self._cr, 'skip_parent_recompute', False)
            self.env['account.account']._parent_store_compute()
        return account_template

    @api.multi
    def write(self, vals):
        field_list = ['name', 'code', 'type', 'currency_id',
                      'user_type', 'reconcile', 'parent_id']
        account_vals = {}
        for field in field_list:
            if field in vals:
                account_vals[field] = vals[field]
        if account_vals and self.suspend_security().account_ids:
            self.suspend_security().account_ids.write(account_vals)
        return super(AccountAccountTemplate, self).write(vals)

    def search(self, cr, uid, domain,
               offset=0, limit=None, order=None, context=None, count=False):
        context = dict(context or {})
        if context.get('force_id_for_search'):
            domain = [('id', '=', context.get('force_id_for_search'))]
        return super(AccountAccountTemplate, self).search(
            cr, uid, domain, offset=offset, limit=limit, order=order,
            context=context, count=count)

    @api.multi
    def unlink(self):
        for record in self:
            for account in record.suspend_security().account_ids:
                account.unlink()
        return super(AccountAccountTemplate, self).unlink()
