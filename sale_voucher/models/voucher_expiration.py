# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class ExpiredVoucher(orm.Model):
    _name = 'expired.voucher'
    _description = 'Voucher that will be expired soon ro already expired'

    _order = 'voucher_date'

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Partner', required=True),
        'debit': fields.float(
            'Debit', digits_compute=dp.get_precision('Account')),
        'credit': fields.float(
            'Credit', digits_compute=dp.get_precision('Account')),
        'balance': fields.float(
            'Balance', digits_compute=dp.get_precision('Account')),
        'voucher_date': fields.date('Voucher date'),
        'last_use_date': fields.date('Last use date'),
        'expiration_date': fields.date('Expiration date', readonly=True),
        'extension_date': fields.date('Extension date'),
        'state': fields.selection([
            ('expire_soon', 'Expire Soon'),
            ('expired', 'Expired'),
            ('reversed', 'Reversed')], 'State',
            required=True),
        'partner_notified': fields.boolean('Partner notified'),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
    }

    def _check_open_voucher(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            voucher_ids = self.search(
                cr, uid,
                [('partner_id', '=', voucher.partner_id.id),
                 ('state', '!=', 'reversed')],
                context=context)
            if len(voucher_ids) > 1:
                raise orm.except_orm(
                    _('User Error'),
                    _("You can only have one voucher in state different "
                      "than 'reversed' for the partner %s")
                    % voucher.partner_id.id)
        return True

    _constraints = [
        (_check_open_voucher, 'Error', ['partner_id', 'state'])
    ]

    def open_move_lines(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'only one record can be processed'
        line = self.browse(cr, uid, ids[0], context=context)
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        voucher_account_id = user.company_id.voucher_account_id.id
        line_ids = self.pool['account.move.line'].search(
            cr, uid,
            [('partner_id', '=', line.partner_id.id),
             ('account_id', '=', voucher_account_id)],
            context=context)
        return {
            'name': 'Account Move Lines',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'domain': "[('id','in',[" + ','.join(map(str, line_ids)) + "])]",
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }

    def expiration_warning(self, cr, uid, ids, context=None):
        __, template_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'sale_voucher', 'voucher_expiration_reminder_template')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.partner_notified:
                continue
            self.pool['email.template'].send_mail(
                cr, uid, template_id, voucher.id, force_send=False,
                context=context)
            voucher.write({'partner_notified': True}, context=context)
        return True

    def _create_expired_voucher(self, cr, uid, context=None):
        # TODO support multi company
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        voucher_account_id = company.voucher_account_id.id
        cr.execute("""
            SELECT partner_id AS partner_id,
                sum(debit) AS debit,
                sum(credit) AS credit,
                sum(credit-debit) AS balance,
                min(text_date) AS voucher_date,
                max(text_date) AS last_use_date,
                company_id AS company_id
            FROM account_move_line line
            WHERE account_id = %s AND reconcile_id IS NULL
            AND company_id = %s
            GROUP BY company_id, partner_id
            HAVING sum(credit-debit) > 0
        """, (voucher_account_id, company.id))
        lines = cr.dictfetchall()
        validity_time = company.voucher_validity_time
        warning_time = company.voucher_warning_time
        line_ids = []
        for line_vals in lines:
            last_date = datetime.strptime(line_vals['last_use_date'],
                                          DEFAULT_SERVER_DATE_FORMAT)
            expiration_date = last_date + relativedelta(months=validity_time)
            reminder_date = expiration_date - relativedelta(days=warning_time)
            voucher_ids = self.search(
                cr, uid,
                [('partner_id', '=', line_vals['partner_id']),
                 ('state', '!=', 'reversed')],
                context=context)
            if reminder_date > datetime.now():
                self.unlink(cr, uid, voucher_ids, context=context)
                continue
            line_vals.update({
                'expiration_date': expiration_date.strftime(
                    DEFAULT_SERVER_DATE_FORMAT),
                'state': 'expire_soon'
            })
            if expiration_date < datetime.now():
                line_vals['state'] = 'expired'
            if voucher_ids:
                self.write(cr, uid, voucher_ids[0], line_vals, context=context)
            else:
                self.create(cr, uid, line_vals, context=context)
        return True
