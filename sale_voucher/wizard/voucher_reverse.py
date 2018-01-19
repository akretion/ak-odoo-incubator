# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm
from openerp.tools.translate import _
import csv
import base64
from StringIO import StringIO


class ReverseExpiredVoucher(orm.TransientModel):
    _name = 'reverse.expired.voucher'
    _description = 'Wizard to reverse expired vouchers'

    _columns = {
        'summary_file': fields.binary('Summary file'),
        'summary_file_name': fields.char('File name'),
    }

    def _get_refund_ids(self, cr, uid, line_ids, context=None):
        line_obj = self.pool['account.move.line']
        balance = 0
        refund_ids = []
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            balance -= line.debit
            balance += line.credit
            if line.credit:
                other_line = [x for x in line.move_id.line_id
                                if x.id != line.id][0]
                refund_ids.append(
                    [x.invoice.id for x in other_line.reconcile_id.line_id
                        if x.id != other_line.id][0])
        return balance, refund_ids

    def _prepare_tax_reverse_move(
            self, cr, uid, move_id, partner_id, fiscal_position, tax,
            context=None):
        fposition_obj = self.pool['account.fiscal.position']
        tax_account_id = fposition_obj.map_account(
            cr, uid, fiscal_position, tax['account_paid_id'],
            context=context)
        return {
            'name': tax['name'],
            'move_id': move_id,
            'credit': tax['amount'],
            'account_id': tax_account_id,
            'partner_id': partner_id,
        }

    def _prepare_reverse_move(
            self, cr, uid, move_id, partner_id, account_id, tax_vals,
            context=None):
        return {
            'name': u'Expiration crédit magasin',
            'move_id': move_id,
            'credit': tax_vals['total'],
            'account_id': account_id,
            'partner_id': partner_id,
        }

    def _get_reverse_journal(self, cr, uid, company, context=None):
        voucher_account_id = company.voucher_account_id.id
        return self.pool['account.journal'].search(cr, uid, [
            ('default_credit_account_id', '=', voucher_account_id),
            ], context=context)[0]

    def _reverse_voucher(self, cr, uid, partner, context=None):
        invoice_obj = self.pool['account.invoice']
        move_obj = self.pool['account.move']
        line_obj = self.pool['account.move.line']
        fposition_obj = self.pool['account.fiscal.position']
        tax_obj = self.pool['account.tax']
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        partner_id = partner.id
        voucher_account_id = company.voucher_account_id.id
        reverse_account_id = company.voucher_reverse_account_id.id
        journal_id = self._get_reverse_journal(
            cr, uid, company, context=context)
        period_id = move_obj._get_period(cr, uid, context=context)
        line_ids = line_obj.search(
            cr, uid, [
                ('partner_id', '=', partner_id),
                ('reconcile_id', '=', False),
                ('account_id', '=', voucher_account_id),
                ('company_id', '=', company.id)],
            context=context)
        balance, refund_ids = self._get_refund_ids(cr, uid, line_ids, context=context)
        refund_ids = invoice_obj.search(
            cr, uid, [('id', 'in', refund_ids)],
            order='date_invoice desc', context=context)
        reverse_amounts = []
        residual = balance
        for refund in invoice_obj.browse(cr, uid, refund_ids, context=context):
            if refund.amount_total >= residual:
                reverse_amounts.append((
                    refund, residual))
                break
            else:
                reverse_amounts.append((
                    refund, refund.amount_total))
                residual -= refund.amount_total
        move_vals = {
            'ref': u'Expiration crédit magasin',
            'journal_id': journal_id,
            'state': 'draft',
            'period_id': period_id,
            'date': fields.date.context_today(self,cr,uid,context=context),
        }
        move_id = move_obj.create(cr, uid, move_vals, context=context)
        voucher_vals = {
            'name': u'Expiration crédit magasin',
            'move_id': move_id,
            'debit': balance,
            'account_id': voucher_account_id,
            'partner_id': partner_id,
        }
        voucher_line_id = line_obj.create(
            cr, uid, voucher_vals, context=context)
        for refund, amount in reverse_amounts:
            account_id = fposition_obj.map_account(
                cr, uid, refund.fiscal_position, reverse_account_id,
                context=context)
            taxes = []
            for line in refund.invoice_line:
                taxes += line.invoice_line_tax_id
            taxes = list(set(taxes))
            tax_vals = tax_obj.compute_all(
                cr, uid, taxes, amount, 1, None, partner)
            for tax in tax_vals['taxes']:
                tax_reverse_vals = self._prepare_tax_reverse_move(
                    cr, uid, move_id, partner_id, refund.fiscal_position, tax,
                    context=context)
                tax_reverse_line_id = line_obj.create(
                    cr, uid, tax_reverse_vals, context=context)
            reverse_vals = self._prepare_reverse_move(
                cr, uid, move_id, partner_id, account_id, tax_vals,
                context=context)
            reverse_line_id = line_obj.create(
                cr, uid, reverse_vals, context=context)
        reconcile_ids = line_ids + [voucher_line_id]
        line_obj.reconcile(cr, uid, reconcile_ids, context=context)
        move_obj.button_validate(cr, uid, [move_id], context=context)
        return balance

    def reverse_expired_vouchers(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        voucher_obj = self.pool['expired.voucher']
        voucher_ids = context.get('active_ids')
        __, template_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'sale_voucher', 'expired_voucher_template')
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(['Client', 'Email', 'Montant'])
        for voucher in voucher_obj.browse(cr, uid, voucher_ids, context=context):
            balance = self._reverse_voucher(cr, uid, voucher.partner_id)
            voucher.write({'state': 'reversed'})
            writer.writerow([
                voucher.partner_id.name.encode('utf-8'),
                voucher.partner_id.email.encode('utf-8'),
                balance])
#            self.pool['email.template'].send_mail(
#                cr, uid, template_id, voucher.id, force_send=False,
#                context=context)
        summary_file = base64.b64encode(f.getvalue())
        file_name = "voucher_reversed.csv"
        self.write(
            cr, uid, ids[0],
            {'summary_file': summary_file, 'summary_file_name': file_name},
            context=context)
        return {
            'name': 'Reverse expired voucher',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reverse.expired.voucher',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0],
            'nodestroy': True
        }
