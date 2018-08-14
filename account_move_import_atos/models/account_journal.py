# -*- coding: utf-8 -*-
# Copyright 2012-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


# from odoo.tools.translate import _
from odoo import models, fields


class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = ['account.journal', 'mail.thread']

    import_type = fields.Selection(
        selection_add=[
            ('atos_csvparser', 'Parser for Atos/Sips (mercanet) xls file')])

    # def _add_special_line(self, cursor, uid, statement_id, parser, result_row_list, profile, context=None):
    #     super(AccountStatementProfil, self)._add_special_line(cursor, uid, statement_id, parser, result_row_list, profile, context=context)
    #     if parser.parser_for('mercanet_csvparser') and parser.get_refund_amount():
    #         partner_id = profile.partner_id and profile.partner_id.id or False
    #         transfer_account_id = profile.internal_account_transfer_id.id or False
    #         statement_line_obj = self.pool.get('account.bank.statement.line')
    #         transfer_vals = {
    #             'name': _('Transfer'),
    #             'date': parser.get_statement_date(),
    #             'amount': parser.get_refund_amount(),
    #             'partner_id': partner_id,
    #             'type': 'general',
    #             'statement_id': statement_id,
    #             'account_id': transfer_account_id,
    #             'ref': 'transfer',
    #             # !! We set the already_completed so auto-completion will not update those values !
    #             'already_completed': True,
    #         statement_line_obj.create(cursor, uid, transfer_vals, context=context)
