# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.osv import fields, osv, orm
import logging

_logger = logging.getLogger(__name__)


class AccountEasyReconcileMethod(orm.Model):
    _inherit = 'account.easy.reconcile.method'

    def _get_all_rec_method(self, cr, uid, context=None):
        res = super(AccountEasyReconcileMethod, self)._get_all_rec_method(
            cr, uid, context=context)
        res.append(
            ('easy.reconcile.all.move.partner', 'All move per Partner'))
        return res


class EasyReconcileAllMovePartner(orm.TransientModel):
    _name = 'easy.reconcile.all.move.partner'
    _inherit = 'easy.reconcile.base'
    _auto = True  # False when inherited from AbstractModel

    def _action_rec(self, cr, uid, rec, context=None):
        """Match all move lines of a partner, do not allow partial reconcile"""
        res = []
        query = \
        """SELECT partner_id FROM account_move_line
            WHERE account_id=%s AND reconcile_id is NULL
            GROUP BY partner_id
            HAVING sum(debit) = sum(credit) AND count(id) > 1
        """
        move_line_obj = self.pool['account.move.line']
        params = (rec.account_id.id,)
        cr.execute(query, params)
        partner_ids = cr.fetchall()
        commit_count = 0
        for partner_id in partner_ids:
            line_ids = move_line_obj.search(cr, uid, [
                ('partner_id', '=', partner_id[0]),
                ('account_id', '=', rec.account_id.id),
                ('reconcile_id', '=', False),
                ], context=context)
            if line_ids:
                commit_count += 1
                move_line_obj.reconcile(
                    cr, uid,
                    line_ids,
                    type='auto',
                    context=context)
                res += line_ids
                if context['commit_every'] \
                        and commit_count % context['commit_every'] == 0:
                    cr.commit()
                    _logger.info(
                        "Commit the reconciliations after %d lines",
                        commit_count)
        return res, []
