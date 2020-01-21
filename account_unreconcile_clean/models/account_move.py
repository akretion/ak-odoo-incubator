# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_writeoff = fields.Boolean(default=False)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_writeoff = fields.Boolean(related="move_id.is_writeoff", readonly=True)

    def _create_writeoff(self, vals):
        return super(
            AccountMoveLine, self.with_context(default_is_writeoff=True)
            )._create_writeoff(vals)

    def _is_move_deletable(self):
        self.ensure_one()
        for line in self.move_id.line_ids:
            if line != self and (line.matched_debit_ids or line.matched_credit_ids):
                return False
        return True

    def _get_related_lines(self):
        all_lines = self.mapped('matched_debit_ids.debit_move_id')\
                + self.mapped('matched_credit_ids.credit_move_id')
        all_lines += all_lines.mapped('matched_debit_ids.debit_move_id')\
                + all_lines.mapped('matched_credit_ids.credit_move_id')
        return all_lines

    def _get_deletable_writeoff(self, all_lines):
        return all_lines.filtered('is_writeoff').filtered(
            lambda s: s._is_move_deletable())

    def _is_exchange(self):
        return self in self.full_reconcile_id.exchange_move_id.line_ids

    def _get_deletable_exchange(self, all_lines):
        return all_lines.filtered(lambda s: s._is_exchange() and s._is_move_deletable())

    def remove_move_reconcile(self):
        all_lines = self._get_related_lines()
        deletable_writeoff = self._get_deletable_writeoff(all_lines)
        deletable_exchange = self._get_deletable_exchange(all_lines)
        deletable = deletable_writeoff + deletable_exchange
        res = super(AccountMoveLine, self + deletable).remove_move_reconcile()
        moves = deletable.mapped('move_id')
        moves.button_cancel()
        moves.unlink()
        return res
