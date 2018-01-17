# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountMoveReconcile(models.Model):
    _inherit = 'account.move.reconcile'

    reconcile_date = fields.Date(
        compute='_compute_reconcile_date',
        store=True)

    def _compute_reconcile_date(self):
        for record in self:
            date = None
            for line in record.line_id:
                date = max(line.date, date)
            record.reconciliation_date = date
