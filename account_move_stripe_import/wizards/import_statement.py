# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class CreditStatementImport(models.TransientModel):
    _inherit = 'credit.statement.import'

    input_statement = fields.Binary(required=False)
    need_file = fields.Boolean(compute='_compute_need_file')

    @api.multi
    def _compute_need_file(self):
        for record in self:
            record.need_file = record.journal_id.import_type != 'stripe'

    @api.multi
    def _check_extension(self):
        if self.need_file:
            return super(CreditStatementImport, self)._check_extension()
        return ''
