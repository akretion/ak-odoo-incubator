# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountMoveReconcile(models.Model):
    _inherit = 'account.move.reconcile'

    date_max = fields.Date(
        compute='_compute_reconcile_date',
        store=True)
    date_min = fields.Date(
        compute='_compute_reconcile_date',
        store=True)

    @api.depends('line_id.date')
    def _compute_reconcile_date(self):
        for record in self:
            min_date = None
            max_date = None
            for line in record.line_id:
                max_date = max(line.date, max_date)
                min_date = min(line.date, min_date)
            record.date_max = max_date
            record.date_min = min_date
